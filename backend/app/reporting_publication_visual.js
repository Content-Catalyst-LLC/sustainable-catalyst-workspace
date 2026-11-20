'use strict';
// SC-PUB-TIPTAP-01: lightweight bridge between the existing authenticated
// Publication Studio and the locally built Tiptap 3 scientific editor.
// The textarea/Markdown is the single authoritative saved revision. When the
// bundle is unavailable, stay in source mode; never pretend visual editing works.

let visualMode = false;
let tiptapBridge = null;

function renderVisualBlocks() {
  if (visualMode && tiptapBridge) tiptapBridge.render();
}

function setEditorMode(mode) {
  const wantVisual = mode === 'visual';
  if (wantVisual && !tiptapBridge) {
    status('Tiptap is not installed in this Reporting Studio image. Markdown source remains available.', true);
    return;
  }
  if (visualMode && !wantVisual) tiptapBridge.destroy();
  visualMode = wantVisual;
  E('visualBlocks').hidden = !visualMode;
  E('visualTools').hidden = !visualMode;
  E('manuscript').hidden = visualMode;
  E('visualMode').setAttribute('aria-pressed', String(visualMode));
  E('sourceMode').setAttribute('aria-pressed', String(!visualMode));
  if (visualMode) tiptapBridge.render();
}

// SC-FIG-PLACE-01: every insertion goes where the researcher put the cursor, in either mode, or nowhere. The Markdown
// cursor counts only when the researcher placed it in the current text (a programmatic value or mode change resets it),
// so an unknown position is refused instead of appended at the end.
const NO_SOURCE_CURSOR = 'Click in the Markdown source where this should go, then insert again. Nothing was inserted.';
let sourceCursor = null;
function rememberSourceCursor() {
  const t = E('manuscript');
  sourceCursor = {value: t.value, start: t.selectionStart, end: t.selectionEnd};
}
for (const type of ['mouseup', 'keyup', 'input']) E('manuscript').addEventListener(type, rememberSourceCursor);
function knownSourceCursor() {
  if (visualMode) setEditorMode('source');  // visual editing unavailable for this manuscript: show the source
  const t = E('manuscript');
  if (!sourceCursor || sourceCursor.value !== t.value) throw Error(NO_SOURCE_CURSOR);
  return sourceCursor;
}
function placeSourceText(at, text) {
  const t = E('manuscript');
  t.setRangeText(text, at, at, 'end');
  rememberSourceCursor();
  markDirty();
}

// [start, end) of each Markdown block; blank lines inside code fences and $$ equations do not end a block.
function sourceBlocks(text) {
  const blocks = [];
  let offset = 0, start = null, last = 0, fence = null, math = false;
  for (const line of text.match(/[^\n]*\n|[^\n]+$/g) || []) {
    const trimmed = line.trim();
    if (!trimmed && !fence && !math) {
      if (start !== null) { blocks.push([start, last]); start = null; }
    } else {
      if (start === null) start = offset;
      last = offset + line.replace(/\n$/, '').length;
      const marker = trimmed.match(/^(`{3,}|~{3,})/);
      if (marker && !fence) fence = marker[1];
      else if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length) fence = null;
      if (!fence && trimmed === '$$') math = !math;
    }
    offset += line.length;
  }
  if (start !== null) blocks.push([start, last]);
  return blocks;
}

// Blocks go between Markdown blocks: before the block when the cursor is at its start, otherwise after it. Never
// inside a sentence, list, table or equation, and never over selected text. Existing bytes are not changed.
function insertSourceBlocks(snippet) {
  const cursor = knownSourceCursor(), text = E('manuscript').value, blocks = sourceBlocks(text);
  const at = cursor.end;
  const inside = blocks.find(([start, end]) => at >= start && at <= end);
  const next = blocks.find(([start]) => start > at);
  if (inside && (at > inside[0] || cursor.start !== cursor.end)) placeSourceText(inside[1], '\n\n' + snippet);
  else if (inside || next) placeSourceText((inside || next)[0], snippet + '\n\n');
  else if (blocks.length) placeSourceText(blocks[blocks.length - 1][1], '\n\n' + snippet);
  else placeSourceText(0, snippet + '\n');
}

function figureAssets(markdown) {
  return [...markdown.matchAll(/!\[[^\]]*\]\(asset:([A-Za-z0-9_.-]+)\)/g)].map(m => m[1]);
}

// The one path for block insertions (figures, scientific outputs, + block buttons): a figure already in the manuscript
// is refused rather than duplicated.
function insertManuscriptBlocks(snippet) {
  const present = new Set(figureAssets(E('manuscript').value));
  const repeated = figureAssets(snippet).filter(id => present.has(id));
  if (repeated.length) {
    throw Error('This figure is already in the manuscript (' + repeated.join(', ') + '). Nothing was inserted; ' +
                'move or delete the existing copy instead.');
  }
  if (!(visualMode && tiptapBridge && tiptapBridge.insertBlocks(snippet))) insertSourceBlocks(snippet);
}

function insertManuscriptCitation(key) {
  if (visualMode && tiptapBridge && tiptapBridge.insertCitation(key)) return;
  const cursor = knownSourceCursor(), t = E('manuscript'), at = cursor.start;
  const lead = at > 0 && !/\s/.test(t.value[at - 1]) ? ' ' : '';
  t.setRangeText(lead + '[@' + key + ']', at, cursor.end, 'end');
  rememberSourceCursor();
  markDirty();
}

// Host services for the single-document editor (SC-EDITOR-DOCX-01).
window.SCStudioAssetUrl = id => path('/assets/' + encodeURIComponent(id) + '/image');
window.SCStudioCitations = () => (state.citations || []).map(item => ({
  key: item.key,
  label: item.formatted[E('citeStyle').value].inText + ' ' + (item.title || '').slice(0, 70),
}));
window.SCStudioCitationLabel = key => {
  const item = (state.citations || []).find(x => x.key === key);
  return item ? item.formatted[E('citeStyle').value].reference.replace(/\*([^*]+)\*/g, '$1') : '';
};

function addVisualMarkdown(snippet) {
  try {
    insertManuscriptBlocks(snippet);
  } catch (error) {
    status(error.message, true);
    return false;
  }
  preview().catch(error => status(error.message, true));
  return true;
}

window.SCStudioRegisterTiptap = function(adapter) {
  if (!adapter || typeof adapter.render !== 'function' || typeof adapter.destroy !== 'function') {
    throw Error('Tiptap editor adapter missing lifecycle handlers');
  }
  tiptapBridge = adapter;
  E('visualMode').disabled = false;
  setEditorMode('visual');
};

E('visualMode').disabled = true;
E('visualMode').onclick = () => setEditorMode('visual');
E('sourceMode').onclick = () => setEditorMode('source');
E('addHeading').onclick = () => addVisualMarkdown('## New section');
E('addParagraph').onclick = () => addVisualMarkdown('New paragraph');
E('addList').onclick = () => addVisualMarkdown('- New item');
E('addQuote').onclick = () => addVisualMarkdown('> Quoted passage');
E('addEquation').onclick = () => {
  if (!addVisualMarkdown('$$\n\n$$')) return;
  setEditorMode('source');
  E('manuscript').focus();
};
setEditorMode('source');
