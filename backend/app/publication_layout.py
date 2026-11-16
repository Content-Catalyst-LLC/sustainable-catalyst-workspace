"""SC-PUB-LAYOUT-01: deterministic scientific figure placement audit and draft repair.

A saved publication's Markdown and verified source objects are immutable.
This module only reports layout problems or proposes a new *unsaved* Markdown
draft after an owner explicitly binds a marker to a project-owned SVG.
No source-body or figure-content inference is permitted.
"""
from __future__ import annotations

import hashlib
import re

FIGURE_LINE = re.compile(r'^!\[([^\]]{0,160})\]\(asset:([A-Za-z0-9_.-]{1,160})\)$')
FIGURE_MARKER = re.compile(r'^\[(FIGURE_[A-Z0-9_]{1,64})\]$')
HEADING = re.compile(r'^(#{1,4})\s+(.+?)\s*$')


def _normalized(value: str) -> str:
    return ' '.join(value.split()).casefold()


def _content_lines(markdown: str):
    """Walk lines, excluding fenced code and display math from layout directives."""
    fenced = False
    math = False
    for number, line in enumerate(markdown.splitlines(), 1):
        value = line.strip()
        if value.startswith('```'):
            fenced = not fenced
            continue
        if not fenced and value == '$$':
            math = not math
            continue
        if not fenced and not math:
            yield number, value


def audit_layout(markdown: str, title: str) -> dict:
    """Report only observed structural problems. Never guess a marker-to-asset mapping."""
    markers = []
    references = []
    first_content = None
    references_section = False
    duplicate_title = False

    for line, value in _content_lines(markdown):
        if not value:
            continue
        if first_content is None:
            first_content = value
            match = HEADING.fullmatch(value)
            duplicate_title = bool(match and len(match.group(1)) == 1
                                   and _normalized(match.group(2)) == _normalized(title))
        heading = HEADING.fullmatch(value)
        if heading and len(heading.group(1)) <= 2 and _normalized(heading.group(2)) in ('references', 'bibliography'):
            references_section = True
        marker = FIGURE_MARKER.fullmatch(value)
        if marker:
            markers.append({'marker': marker.group(1), 'line': line})
        figure = FIGURE_LINE.fullmatch(value)
        if figure:
            references.append({'assetId': figure.group(2), 'caption': figure.group(1),
                               'line': line, 'afterReferences': references_section})

    issues = []
    if duplicate_title:
        issues.append({'code': 'repeated-document-title', 'severity': 'info', 'line': 1,
                       'message': 'The first manuscript heading duplicates the publication title; exports show the title only once.'})
    for marker in markers:
        issues.append({'code': 'unresolved-figure-marker', 'severity': 'error',
                       'line': marker['line'], 'marker': marker['marker'],
                       'message': 'Choose a verified SVG asset for this marker. No scientific figure can be inferred automatically.'})
    by_id = {}
    for figure in references:
        by_id.setdefault(figure['assetId'], []).append(figure)
        if figure['afterReferences']:
            issues.append({'code': 'figure-after-references', 'severity': 'warning',
                           'line': figure['line'], 'assetId': figure['assetId'],
                           'message': 'The figure is placed within or after the references section.'})
    for aid, entries in by_id.items():
        if len(entries) > 1:
            issues.append({'code': 'repeated-figure-asset', 'severity': 'warning',
                           'line': entries[1]['line'], 'assetId': aid,
                           'occurrences': len(entries),
                           'message': 'This source figure occurs multiple times. Confirm whether repetition is intentional.'})

    return {
        'status': 'needs-attention' if any(i['severity'] != 'info' for i in issues) else 'ready',
        'markdownSHA256': hashlib.sha256(markdown.encode()).hexdigest(),
        'titleDeduplicatedInExport': duplicate_title,
        'markers': markers, 'figures': references, 'issues': issues,
        'figureOccurrences': len(references),
        'distinctFigureAssets': len(by_id),
    }


def without_repeated_title(blocks: list[dict], title: str) -> list[dict]:
    """Presentation-only suppression for an exact leading H1 equal to the document title."""
    if (blocks and blocks[0]['kind'] == 'heading' and blocks[0]['level'] == 1
            and _normalized(blocks[0]['text']) == _normalized(title)):
        return blocks[1:]
    return blocks


def propose_figure_move(markdown: str, marker: str, asset_id: str,
                        caption: str = '') -> dict:
    """Make one explicit placement; return proposed source without saving.

    Multiple existing identical placements are removed only when an owner
    explicitly chooses that exact asset and a single destination marker.
    Conflicting original captions are not silently reconciled.
    """
    if not FIGURE_MARKER.fullmatch('[' + marker + ']'):
        raise ValueError('Choose a valid named figure marker.')
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}', asset_id):
        raise ValueError('Choose a valid figure asset ID.')
    if len(caption) > 160 or '\n' in caption or '\r' in caption or ']' in caption:
        raise ValueError('Figure caption contains invalid characters.')

    lines = markdown.splitlines(keepends=True)
    destinations = []
    removals = []
    captured = []
    # Use offset-by-line rather than reserializing the whole Markdown source:
    # untouched lines (including their original line endings) stay byte-for-byte.
    eligible = set(n for n, _ in _content_lines(markdown))
    for ix, source in enumerate(lines):
        if ix + 1 not in eligible:
            continue
        value = source.strip()
        if value == '[' + marker + ']':
            destinations.append(ix)
        figure = FIGURE_LINE.fullmatch(value)
        if figure and figure.group(2) == asset_id:
            removals.append(ix)
            captured.append(figure.group(1))
    if len(destinations) != 1:
        raise ValueError('The selected figure marker must appear exactly once in the manuscript.')
    if len(set(captured)) > 1:
        raise ValueError('Existing figure placements have conflicting captions; review manually.')
    selected_caption = captured[0] if captured else caption.strip()
    if not selected_caption:
        raise ValueError('Supply a figure caption before placing a new asset.')
    if ']' in selected_caption:
        raise ValueError('Existing figure caption is not a valid Markdown caption.')

    destination = destinations[0]
    replacement = f'![{selected_caption}](asset:{asset_id})'
    output = []
    for ix, source in enumerate(lines):
        if ix in removals:
            continue
        if ix == destination:
            eol = '\r\n' if source.endswith('\r\n') else ('\n' if source.endswith('\n') else '')
            output.append(replacement + eol)
        else:
            output.append(source)
    proposed = ''.join(output)
    return {
        'markdown': proposed,
        'beforeSHA256': hashlib.sha256(markdown.encode()).hexdigest(),
        'afterSHA256': hashlib.sha256(proposed.encode()).hexdigest(),
        'marker': marker,
        'assetId': asset_id,
        'caption': selected_caption,
        'removedDuplicatePlacements': max(0, len(removals) - 1),
        'movedExistingPlacements': len(removals),
    }
