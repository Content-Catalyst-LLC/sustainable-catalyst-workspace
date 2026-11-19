/**
 * SC-PUB-TIPTAP-01: reversible Markdown block boundaries.
 *
 * Tiptap edits only an explicitly supported block. All other blocks, plus
 * their separators, are kept byte-for-byte until the researcher edits them
 * in the existing Markdown source editor. Never normalize an entire saved
 * scientific manuscript through the beta Markdown extension.
 */
export function splitMarkdown(source) {
  if (typeof source !== 'string') throw TypeError('Expected a Markdown string');
  const lines = source.match(/[^\n]*\n|[^\n]+$/g) || [];
  const parts = [];
  let prefix = '', raw = '', fence = null, inMath = false;
  for (const line of lines) {
    const trimmed = line.trim();
    if (!raw && !trimmed && !parts.length) {
      prefix += line;
      continue;
    }
    if (!fence && !inMath && !trimmed) {
      if (raw) { parts.push({ raw, separator: line }); raw = ''; }
      else if (parts.length) parts[parts.length - 1].separator += line;
      else prefix += line;
      continue;
    }
    raw += line;
    const marker = trimmed.match(/^(\x60{3,}|~{3,})/);
    if (marker) {
      const char = marker[1][0];
      if (!fence) fence = { char, size: marker[1].length };
      else if (fence.char === char && marker[1].length >= fence.size) fence = null;
    }
    if (!fence && trimmed === '$$') inMath = !inMath;
  }
  if (raw) parts.push({raw, separator: ''});
  return {prefix, parts};
}

export function joinMarkdown(prefix, parts) {
  return prefix + parts.map(x => x.raw + x.separator).join('');
}

const GFM_TABLE = /^\|[^\n]*\|[ \t]*\n\|[ \t:|-]*-{3,}[ \t:|-]*\|?[ \t]*(?:\n\|[^\n]*\|[ \t]*)*\n?$/;
// Scientific syntax that must never pass through the beta Markdown parser,
// whether it stands alone or sits inside an otherwise editable table.
const SCIENTIFIC_SOURCE = [
  /<[/!]?[A-Za-z][^>]*>/,
  /!\[[^\]]*\]\(/,
  /(?<!\\)\$[^$\n]+(?<!\\)\$/,
  /\[@[^\]]+\][ \t]*\([^)]+\)/,
];

export function classifyMarkdownBlock(raw) {
  const text = raw.trimEnd();
  if (!text) return 'protected';
  // SC-EDITOR-DOCX-01: a well-formed GFM table (header, separator, rows) is
  // edited as a real table; tables with scientific source stay protected.
  if (GFM_TABLE.test(text + '\n')) {
    return SCIENTIFIC_SOURCE.some(re => re.test(text)) ? 'protected' : 'table';
  }
  // Protect scientific syntax and richer structures not proven safe for
  // Markdown round-trip: source references, equations, figures, other tables,
  // HTML, code, deep/multiline headings, task lists and front matter.
  const protectedPatterns = [
    /(?:^|\n)\s*(?:!\[[^\n]*\]|[|]|:{3,}|\$\$|\\\[|\\\]|\\\(|\\\)|\x60{3,}|~{3,}|-{3,}\s*$)/,
    /(?:^|\n)\s{4,}\S/,
    /(?:^|\n)#{5,6}\s/,
    /(?:^|\n)\s*-\s*\[[ xX]\]/,
    /(?:^|\n)\s*\[\^[^\]]+\]:/,
    /(?:^|\n)\s*[^ \n|\\]+\s*(?<!\\)\|\s*[^ \n|]+/,
    /(?:^|\n)\s*\|?\s*:?-{3,}:?\s*\|/,
    ...SCIENTIFIC_SOURCE,
  ];
  if (protectedPatterns.some(re => re.test(text))) return 'protected';
  // One heading per rich block; a mixed Markdown section is source-only.
  if (/^#{1,4} [^\n]+$/.test(text)) return 'heading';
  if (/(?:^|\n)#{1,6}\s/.test(text)) return 'protected';
  if (text.split('\n').every(line => /^(?: {2}){0,3}(?:[-*+]|\d{1,3}[.)]) [^\n]+/.test(line))) return 'list';
  if (text.split('\n').every(line => /^> ?[^\n]+/.test(line))) return 'quote';
  if (/(?:^|\n)\s*([-+*]\s|\d+\.\s)/.test(text)) return 'protected';
  return 'paragraph';
}

export function replaceEditedBlock(original, markdown) {
  // Preserve source line termination and all untouched neighboring bytes.
  const trailing = original.match(/\n*$/)[0];
  return String(markdown).replace(/\n*$/, '') + trailing;
}


/**
 * Tiptap Markdown escapes square brackets of plain text tokens. Restore
 * exclusively valid Citation Studio markers, otherwise the existing server
 * citation parser would treat a formerly cited revision as unresolved.
 *
 * This is a deliberately narrow compatibility normalization, not a general
 * Markdown unescape or scientific content transformation.
 */
const CITATION_MARKER = /\[@[A-Za-z0-9_.:-]{1,80}(?:,[^;\]\n]{1,40})?(?:;\s*@[A-Za-z0-9_.:-]{1,80}(?:,[^;\]\n]{1,40})?)*\]/g;
const CITATION_EXACT = new RegExp('^' + CITATION_MARKER.source + '$');

export function restoreCitationMarkers(markdown, originalBlock, inserted = []) {
  // Only restore marks that were *already active citations* before this
  // rich-text edit. An intentionally escaped literal marker must NOT become
  // an active citation merely because a neighboring word was changed.
  // Markers the researcher inserted through the editor's Cite command are
  // equally intentional; no other bracketed text is ever activated.
  const allowed = new Set([...(String(originalBlock).match(CITATION_MARKER) || []), ...inserted]);
  return String(markdown).replace(/\\\[([^\]\n]{1,320}?)\\\]/g, (whole, inside) => {
    const candidate = '[' + inside.replace(/\\([_.:*-])/g, '$1') + ']';
    return CITATION_EXACT.test(candidate) && allowed.has(candidate) ? candidate : whole;
  });
}
