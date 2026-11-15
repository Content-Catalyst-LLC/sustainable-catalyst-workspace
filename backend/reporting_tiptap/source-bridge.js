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

export function classifyMarkdownBlock(raw) {
  const text = raw.trimEnd();
  if (!text) return 'protected';
  // Protect scientific syntax and richer structures not proven safe for
  // Markdown round-trip: source references, equations, figures, tables,
  // HTML, code, nested/multiline headings, task lists and front matter.
  const protectedPatterns = [
    /(?:^|\n)\s*(?:!\[[^\n]*\]|[|]|:{3,}|\$\$|\\\[|\\\]|\\\(|\\\)|\x60{3,}|~{3,}|-{3,}\s*$)/,
    /(?:^|\n)\s{4,}\S/,
    /(?:^|\n)#{3,6}\s/,
    /(?:^|\n)\s*-\s*\[[ xX]\]/,
    /(?:^|\n)\s*\[\^[^\]]+\]:/,
    /(?:^|\n)\s*[^ \n|]+\s*\|\s*[^ \n|]+/,
    /(?:^|\n)\s*\|?\s*:?-{3,}:?\s*\|/,
    /<[/!]?[A-Za-z][^>]*>/,
    /!\[[^\]]*\]\(/,
    /(?<!\\)\$[^$\n]+(?<!\\)\$/,
    /\[@[^\]]+\][ \t]*\([^)]+\)/,
  ];
  if (protectedPatterns.some(re => re.test(text))) return 'protected';
  // One heading per rich block; a mixed Markdown section is source-only.
  if (/^#{1,2} [^\n]+$/.test(text)) return 'heading';
  if (/(?:^|\n)#{1,6}\s/.test(text)) return 'protected';
  if (text.split('\n').every(line => /^[-*] [^\n]+/.test(line))) return 'list';
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
export function restoreCitationMarkers(markdown) {
  return String(markdown).replace(/\\\[@([A-Za-z0-9_.:-]{1,80})\\\]/g, '[@$1]');
}
