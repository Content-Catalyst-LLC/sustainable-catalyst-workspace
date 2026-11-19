"""SC-EDITOR-DOCX-01: structure-aware DOCX -> Publication Studio manuscript conversion.

Replaces the text-only extraction for Word manuscripts. Reuses the DOCS-01 viewer's hardened package reader (size
limits, no entity resolution, style/numbering/footnote tables) and emits the Studio's strict Markdown subset:
headings, paragraphs with bold/italic/links, bulleted and numbered lists, GFM tables, figures (``asset:`` references
to project-owned images extracted from the package) and the reference list as one entry per paragraph.

The original DOCX bytes are never modified. Anything the subset cannot express is listed in ``unsupported`` so the
owner sees exactly what the editable manuscript does not carry; nothing is dropped silently.
"""
from __future__ import annotations

import hashlib
import re
from typing import Callable

from .research_documents import A, IMAGE_TYPES, R, VML, MATH, CHART, DocxRenderer, _xml, w

CONVERTER = 'sc-docx-manuscript/1.0'
RASTER_TYPES = {'image/png': '.png', 'image/jpeg': '.jpg'}
REFERENCES_HEADING = re.compile(
    r'^(?:list of )?(?:references?|reference list|bibliography|works cited|literature cited|sources cited)$', re.I)
CAPTION_TEXT = re.compile(r'^(?:figure|fig\.?|table|exhibit|chart)\s*\d+', re.I)
MAX_CAPTION = 160
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'


def escape_md(text: str, table: bool = False) -> str:
    """Escape text so the Studio renderer and Tiptap both read it literally."""
    out = re.sub(r'([\\`*\[\]$])', r'\\\1', text)
    out = re.sub(r'(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])', r'\\_', out)
    out = re.sub(r'<(?=[A-Za-z/!])', r'\\<', out)
    if table:
        out = out.replace('|', r'\|')
    return out


def _escape_line_start(text: str) -> str:
    """A paragraph must not turn into a heading, list, quote or table merely because of its first characters."""
    match = re.match(r'^(\s*)(#{1,6}\s|>|[-+*]\s|\d+[.)]\s|\|)', text)
    if not match:
        return text
    lead, token = match.groups()
    if token[0].isdigit():
        digits = re.match(r'\d+', token).group(0)
        return lead + digits + '\\' + token[len(digits):] + text[match.end():]
    return lead + '\\' + token + text[match.end():]


def reference_entries(blocks: list[tuple[str, dict]]) -> list[int]:
    """Indexes of paragraph blocks that sit under a references heading (until the next heading at that level)."""
    found, level = [], None
    for index, (kind, data) in enumerate(blocks):
        if kind == 'heading':
            if REFERENCES_HEADING.match(data['text'].strip().rstrip(':')):
                level = data['level']
            elif level is not None and data['level'] <= level:
                level = None
        elif kind == 'paragraph' and level is not None:
            found.append(index)
    return found


class DocxToManuscript(DocxRenderer):
    """Converts the package once; ``figure_id`` maps an extracted image to the project asset id it is stored as."""

    def __init__(self, raw: bytes, figure_id: Callable[[dict], str] | None = None):
        super().__init__(raw)
        self.source_sha256 = hashlib.sha256(raw).hexdigest()
        self.figure_id = figure_id or (lambda media: 'docx-figure-' + media['sha256'][:24])
        self.media: list[dict] = []
        self.blocks_out: list[tuple[str, dict]] = []
        self.unsupported: dict[str, dict] = {}
        self.notes: list[str] = []
        self.title = ''
        self.heading_offset = 0
        self._pending_drawings: list[dict] = []

    # Reporting -------------------------------------------------------------------------------------------------

    def _flag(self, feature: str, detail: str, count: int = 1):
        entry = self.unsupported.setdefault(feature, {'feature': feature, 'count': 0, 'detail': detail})
        entry['count'] += count

    # Package-level analysis -------------------------------------------------------------------------------------

    def convert(self) -> dict:
        root = _xml(self.pkg.read('word/document.xml'))
        body = root.find(w('body'))
        children = list(self._flatten(body if body is not None else []))
        self._detect_title(children)
        self._scan_unsupported(root)
        for node in children:
            if node.tag == w('p'):
                self._paragraph(node)
            elif node.tag == w('tbl'):
                self._table(node)
        self._attach_captions()
        if self.used_notes:
            self.blocks_out.append(('heading', {'level': 2, 'text': 'Notes', 'md': 'Notes'}))
            for n, ident in enumerate(self.used_notes, 1):
                text = ' '.join(self._inline_md(p) for p in self.footnotes[ident].iter(w('p'))).strip()
                self.blocks_out.append(('paragraph', {'md': f'{n}\\. ' + text, 'text': text}))
            self._flag('footnotes', 'Footnotes become numbered text markers with a Notes section; Word footnote '
                                    'objects are not recreated.', len(self.used_notes))
        refs = reference_entries(self.blocks_out)
        for index in refs:
            self.blocks_out[index][1]['reference'] = True
        markdown = '\n\n'.join(self._block_md(kind, data) for kind, data in self.blocks_out).strip() + '\n'
        headings = [(d['level'], d['text']) for k, d in self.blocks_out if k == 'heading']
        tables = [(len(d['rows']), max((len(r) for r in d['rows']), default=0)) for k, d in self.blocks_out if k == 'table']
        return {
            'converter': CONVERTER, 'sourceSha256': self.source_sha256, 'title': self.title, 'markdown': markdown,
            'markdownSha256': hashlib.sha256(markdown.encode()).hexdigest(),
            'media': self.media,
            'outline': {'headings': headings, 'tables': tables, 'figures': sum(1 for k, _ in self.blocks_out if k == 'figure'),
                        'referenceEntries': len(refs),
                        'paragraphs': sum(1 for k, _ in self.blocks_out if k == 'paragraph'),
                        'lists': sum(1 for k, _ in self.blocks_out if k == 'list')},
            'unsupported': sorted(self.unsupported.values(), key=lambda x: x['feature']),
            'notes': self.notes,
        }

    def _flatten(self, parent):
        for node in parent:
            if node.tag == w('sdt'):
                content = node.find(w('sdtContent'))
                if content is not None:
                    yield from self._flatten(content)
            elif node.tag in (w('p'), w('tbl')):
                yield node

    def _scan_unsupported(self, root):
        checks = [
            (f'.//{{{MATH}}}oMath', 'equations', 'Word (OMML) equations are not converted; a marker is left in place.'),
            (f'.//{w("txbxContent")}', 'text boxes', 'Text boxes and floating shapes are not part of the manuscript flow.'),
            (f'.//{{{CHART}}}chart', 'charts', 'Native Word charts are not converted; export the chart as an image.'),
            (f'.//{w("del")}', 'tracked deletions', 'Tracked deletions are excluded (the accepted text is imported).'),
            (f'.//{w("ins")}', 'tracked insertions', 'Tracked insertions are imported as accepted text.'),
            (f'.//{w("commentRangeStart")}', 'comments', 'Word comments are not imported.'),
            (f'.//{w("br")}[@{w("type")}="page"]', 'page breaks', 'Page breaks are not represented; export paginates.'),
            (f'.//{w("vertAlign")}', 'superscript/subscript', 'Superscript and subscript become plain text.'),
            (f'.//{w("u")}', 'underline', 'Underline becomes plain text.'),
            (f'.//{w("strike")}', 'strikethrough', 'Strikethrough becomes plain text.'),
            (f'.//{w("fldSimple")}', 'fields', 'Fields (e.g. automatic numbering, TOC) are imported as their current text.'),
            (f'.//{w("instrText")}', 'fields', 'Fields (e.g. automatic numbering, TOC) are imported as their current text.'),
        ]
        for path, feature, detail in checks:
            count = len(root.findall(path))
            if feature in ('superscript/subscript',):
                count = sum(1 for v in root.findall(path) if v.get(w('val')) in ('superscript', 'subscript'))
            if feature in ('underline', 'strikethrough'):
                count = sum(1 for v in root.findall(path) if v.get(w('val')) not in ('0', 'false', 'none'))
            if count:
                self._flag(feature, detail, count)
        sect = root.find(f'.//{w("sectPr")}')
        if sect is not None and (sect.find(w('headerReference')) is not None or sect.find(w('footerReference')) is not None):
            self._flag('headers and footers', 'Page headers and footers are not imported; exports use Studio headers.')

    # Title and styles -------------------------------------------------------------------------------------------

    def _style(self, p) -> str:
        ps = p.find(f'{w("pPr")}/{w("pStyle")}')
        return self.styles.get(ps.get(w('val')), ps.get(w('val'), '')).lower() if ps is not None else ''

    def _heading_level(self, style: str, p) -> int | None:
        match = re.fullmatch(r'heading ([1-9])', style)
        if match:
            return int(match.group(1))
        lvl = p.find(f'{w("pPr")}/{w("outlineLvl")}')
        if lvl is not None and (lvl.get(w('val')) or '').isdigit() and int(lvl.get(w('val'))) < 9:
            return int(lvl.get(w('val'))) + 1
        return None

    def _detect_title(self, children):
        """Use the Title style; otherwise a leading bold, large or centred paragraph before the first heading."""
        for p in children:
            if p.tag != w('p'):
                return
            style = self._style(p)
            text = self._plain(p).strip()
            if style == 'title' and text:
                self._title_node, self.title, self.heading_offset = p, text, 1
                return
            if self._heading_level(style, p) is not None:
                return
            if not text:
                continue
            runs = [r for r in p.iter(w('r')) if ''.join(t.text or '' for t in r.iter(w('t'))).strip()]
            sizes = [int(s.get(w('val'))) for r in runs for s in r.findall(f'{w("rPr")}/{w("sz")}')
                     if (s.get(w('val')) or '').isdigit()]
            bold = bool(runs) and all(self._on(r, 'b') for r in runs)
            jc = p.find(f'{w("pPr")}/{w("jc")}')
            centred = jc is not None and jc.get(w('val')) == 'center'
            large = bool(sizes) and min(sizes) >= 32  # half-points: 16 pt
            if len(text) <= 300 and ((bold and (large or centred)) or (large and centred)):
                self._title_node, self.title, self.heading_offset = p, text, 1
                self.notes.append('Title inferred from its formatting (' + ', '.join(
                    x for x, on in (('bold', bold), (f'{max(sizes) / 2:g} pt' if sizes else '', large),
                                    ('centred', centred)) if on and x) + ').')
            return

    def _list_kind(self, p) -> str | None:
        """Direct numbering first; otherwise Word's list styles (List Bullet / List Number), which number via the style."""
        kind = super()._list_kind(p)
        if kind:
            return kind
        style = self._style(p)
        return 'ul' if style.startswith('list bullet') else 'ol' if style.startswith('list number') else None

    @staticmethod
    def _on(r, tag) -> bool:
        el = r.find(f'{w("rPr")}/{w(tag)}')
        return el is not None and el.get(w('val')) not in ('0', 'false', 'none')

    def _plain(self, node) -> str:
        return ''.join(t.text or '' for t in node.iter(w('t')))

    # Inline -----------------------------------------------------------------------------------------------------

    def _segments(self, parent, link: str | None = None):
        for node in parent:
            tag = node.tag
            if tag == w('r'):
                yield from self._run_segments(node, link)
            elif tag == w('hyperlink'):
                target = self.rels.get(node.get(f'{{{R}}}id'), ('', ''))
                url = target[0] if target[1] == 'External' and re.match(r'^(https?://|mailto:)', target[0]) else None
                if node.get(f'{{{R}}}id') and url is None:
                    self._flag('internal links', 'Bookmarks and non-web links are imported as plain text.')
                yield from self._segments(node, url or link)
            elif tag in (w('ins'), w('smartTag'), w('fldSimple'), w('customXml')):
                yield from self._segments(node, link)
            elif tag == w('sdt'):
                content = node.find(w('sdtContent'))
                if content is not None:
                    yield from self._segments(content, link)
            elif tag == f'{{{MATH}}}oMath' or tag == f'{{{MATH}}}oMathPara':
                yield ('[Equation not converted]', False, False, None)

    def _run_segments(self, r, link):
        bold, italic = self._on(r, 'b'), self._on(r, 'i')
        for node in r:
            tag = node.tag
            if tag == w('t'):
                yield (node.text or '', bold, italic, link)
            elif tag in (w('tab'), w('br'), w('cr')):
                if tag == w('br') and node.get(w('type')) == 'page':
                    continue
                yield (' ', False, False, link)
            elif tag == w('noBreakHyphen'):
                yield ('‑', bold, italic, link)
            elif tag == w('drawing'):
                self._drawing(node)
            elif tag == w('pict'):
                data = node.find(f'.//{{{VML}}}imagedata')
                if data is not None:
                    self._image(data.get(f'{{{R}}}id'), data.get('title', ''), None)
            elif tag == w('footnoteReference'):
                ident = node.get(w('id'))
                if ident in self.footnotes:
                    if ident not in self.used_notes:
                        self.used_notes.append(ident)
                    yield (f'[{self.used_notes.index(ident) + 1}]', False, False, None)

    def _inline_md(self, parent, table: bool = False) -> str:
        merged: list[list] = []
        for text, bold, italic, link in self._segments(parent):
            if not text:
                continue
            if merged and merged[-1][1:] == [bold, italic, link]:
                merged[-1][0] += text
            else:
                merged.append([text, bold, italic, link])
        out = []
        for text, bold, italic, link in merged:
            core = text.strip()
            if not core:
                out.append(' ' if text else '')
                continue
            lead, trail = text[:len(text) - len(text.lstrip())], text[len(text.rstrip()):]
            piece = escape_md(core, table)
            if bold and italic:
                piece = f'***{piece}***'
            elif bold:
                piece = f'**{piece}**'
            elif italic:
                piece = f'*{piece}*'
            if link:
                piece = f'[{piece}]({link.replace(")", "%29").replace(" ", "%20")})'
            out.append(lead + piece + trail)
        return re.sub(r'[ \t]+', ' ', ''.join(out)).strip()

    # Figures ----------------------------------------------------------------------------------------------------

    def _drawing(self, node):
        blip = node.find(f'.//{{{A}}}blip')
        doc_pr = node.find(f'.//{{{WP}}}docPr')
        alt = (doc_pr.get('descr') or doc_pr.get('title') or '') if doc_pr is not None else ''
        if blip is None:
            if node.find(f'.//{{{CHART}}}chart') is None:
                self._flag('drawings', 'Shapes and SmartArt are not converted.')
            self._pending_drawings.append({'unsupported': True, 'alt': alt})
            return
        extent = node.find(f'.//{{{WP}}}extent')
        width = int(extent.get('cx')) if extent is not None and (extent.get('cx') or '').isdigit() else None
        self._image(blip.get(f'{{{R}}}embed'), alt, width)

    def _image(self, rid, alt, width_emu):
        target = self.rels.get(rid or '')
        raw = self.pkg.read(target[0]) if target and target[1] != 'External' else None
        media_type = next((m for magic, m in IMAGE_TYPES.items() if raw and raw.startswith(magic)), None)
        if media_type not in RASTER_TYPES:
            self._flag('unsupported images', 'Linked, GIF, EMF/WMF or other non PNG/JPEG images are not extracted; a '
                                             'marker is left at their position.')
            self._pending_drawings.append({'unsupported': True, 'alt': alt})
            return
        digest = hashlib.sha256(raw).hexdigest()
        media = next((m for m in self.media if m['sha256'] == digest), None)
        if media is None:
            media = {'part': target[0], 'sha256': digest, 'bytes': len(raw), 'mediaType': media_type,
                     'extension': RASTER_TYPES[media_type], 'index': len(self.media) + 1, 'raw': raw,
                     'widthEmu': width_emu, 'alt': alt}
            media['assetId'] = self.figure_id(media)
            self.media.append(media)
        self._pending_drawings.append({'media': media, 'alt': alt})

    # Blocks -----------------------------------------------------------------------------------------------------

    def _paragraph(self, p):
        self._pending_drawings = []
        style = self._style(p)
        content = self._inline_md(p)
        drawings, self._pending_drawings = self._pending_drawings, []
        level = self._heading_level(style, p)
        if p is getattr(self, '_title_node', None):
            self.blocks_out.append(('heading', {'level': 1, 'text': self.title, 'md': escape_md(self.title), 'title': True}))
        elif content and level is not None:
            level = min(level + self.heading_offset, 4)
            if level == 4 and (self._heading_level(style, p) or 0) + self.heading_offset > 4:
                self._flag('deep headings', 'Heading levels below the fourth are imported as fourth-level headings.')
            self.blocks_out.append(('heading', {'level': level, 'text': self._plain(p).strip(), 'md': content}))
        elif content:
            kind = self._list_kind(p)
            if kind:
                ilvl = p.find(f'{w("pPr")}/{w("numPr")}/{w("ilvl")}')
                depth = int(ilvl.get(w('val'))) if ilvl is not None and (ilvl.get(w('val')) or '').isdigit() else 0
                item = {'md': content, 'depth': min(depth, 3)}
                if depth:
                    self._flag('nested lists', 'Nested list levels are kept in the editor; exports show them flat.')
                last = self.blocks_out[-1] if self.blocks_out else None
                if last and last[0] == 'list' and last[1]['kind'] == kind:
                    last[1]['items'].append(item)
                else:
                    self.blocks_out.append(('list', {'kind': kind, 'items': [item]}))
            else:
                self.blocks_out.append(('paragraph', {'md': _escape_line_start(content), 'text': self._plain(p).strip(),
                                                      'caption': style == 'caption'}))
        for drawing in drawings:
            if drawing.get('unsupported'):
                self.blocks_out.append(('paragraph', {'md': escape_md('[Figure not converted: unsupported image]'),
                                                      'text': ''}))
            else:
                self.blocks_out.append(('figure', {'media': drawing['media'], 'alt': drawing['alt'], 'caption': ''}))

    def _table(self, tbl):
        rows, merged, nested = [], 0, False
        for tr in tbl.findall(w('tr')):
            cells = []
            for tc in tr.findall(w('tc')):
                pr = tc.find(w('tcPr'))
                span, cont = 1, False
                if pr is not None:
                    gs = pr.find(w('gridSpan'))
                    if gs is not None and (gs.get(w('val')) or '').isdigit():
                        span = max(1, int(gs.get(w('val'))))
                    vm = pr.find(w('vMerge'))
                    cont = vm is not None and (vm.get(w('val')) or 'continue') == 'continue'
                if tc.find(f'.//{w("tbl")}') is not None:
                    nested = True
                text = '' if cont else ' '.join(
                    x for x in (self._inline_md(p, table=True) for p in tc.iter(w('p'))) if x)
                merged += (span - 1) + int(cont)
                cells.extend([text] + [''] * (span - 1))
            rows.append(cells)
        if not rows:
            return
        if merged:
            self._flag('merged table cells', 'Merged cells are split; the content stays in the first cell.', merged)
        if nested:
            self._flag('nested tables', 'Nested tables are flattened into their cell text.')
        width = max(len(r) for r in rows)
        if width > 16:
            self._flag('wide tables', 'Tables wider than 16 columns are truncated in exports.')
        self.blocks_out.append(('table', {'rows': [r + [''] * (width - len(r)) for r in rows]}))

    def _attach_captions(self):
        """A figure takes the caption paragraph directly after it (or directly before it); that paragraph is consumed."""
        out = self.blocks_out
        for i, (kind, data) in enumerate(out):
            if kind != 'figure':
                continue
            for j in (i + 1, i - 1):
                if 0 <= j < len(out) and out[j][0] == 'paragraph' and not out[j][1].get('consumed') and \
                        (out[j][1].get('caption') or CAPTION_TEXT.match(out[j][1]['text'])) and \
                        len(out[j][1]['text']) <= 400:
                    data['caption'] = out[j][1]['text']
                    if len(data['caption']) <= MAX_CAPTION:
                        out[j][1]['consumed'] = True
                    break
            if not data['caption']:
                data['caption'] = data['alt'] or f'Figure {data["media"]["index"]}'
        self.blocks_out = [b for b in out if not b[1].get('consumed')]

    def _block_md(self, kind: str, data: dict) -> str:
        if kind == 'heading':
            return '#' * data['level'] + ' ' + data['md']
        if kind == 'paragraph':
            return data['md']
        if kind == 'list':
            return '\n'.join('  ' * it['depth'] + ('- ' if data['kind'] == 'ul' else '1. ') + it['md']
                             for it in data['items'])
        if kind == 'table':
            rows = data['rows']
            line = lambda r: '| ' + ' | '.join(c or ' ' for c in r) + ' |'
            return '\n'.join([line(rows[0]), '|' + '---|' * len(rows[0])] + [line(r) for r in rows[1:]])
        if kind == 'figure':
            caption = re.sub(r'\s+', ' ', data['caption']).replace('[', '(').replace(']', ')')[:MAX_CAPTION].strip()
            return f'![{caption}](asset:{data["media"]["assetId"]})'
        raise ValueError(kind)


def convert_docx(raw: bytes, figure_id: Callable[[dict], str] | None = None) -> dict:
    return DocxToManuscript(raw, figure_id).convert()
