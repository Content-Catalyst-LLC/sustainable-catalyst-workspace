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
const CITATION_MARKER = /\[@[A-Za-z0-9_.:-]{1,80}(?:,[^;\]\n]{1,40})?(?:;\s*@[A-Za-z0-9_.:-]{1,80}(?:,[^;\]\n]{1,40})?)*\]/g;
const CITATION_EXACT = new RegExp('^' + CITATION_MARKER.source + '$');

export function restoreCitationMarkers(markdown, originalBlock) {
  // Only restore marks that were *already active citations* before this
  // rich-text edit. An intentionally escaped literal marker must NOT become
  // an active citation merely because a neighboring word was changed.
  const allowed = new Set(String(originalBlock).match(CITATION_MARKER) || []);
  return String(markdown).replace(/\\\[([^\]\n]{1,320}?)\\\]/g, (whole, inside) => {
    const candidate = '[' + inside.replace(/\\([_.:*-])/g, '$1') + ']';
    return CITATION_EXACT.test(candidate) && allowed.has(candidate) ? candidate : whole;
  });
}

/**
 * SC-EDITOR-01: prove that opening a block visually cannot rewrite it.
 * A recognized Markdown block is NOT necessarily safe in Tiptap's beta
 * serializer. Refuse visual editing unless the initial parse/serialize cycle
 * returns exactly the original semantic bytes (ignoring the block's terminal
 * newline, which replaceEditedBlock restores separately).
 */
export function isLosslessRichBlock(original, serialized) {
  if (typeof original !== 'string' || typeof serialized !== 'string') return false;
  const trimmed = value => value.replace(/\n+$/, '');
  return trimmed(original) === trimmed(restoreCitationMarkers(serialized, original));
}
