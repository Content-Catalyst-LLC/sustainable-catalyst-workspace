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

function prepareSourceInsertion() {
  if (!visualMode) return;
  setEditorMode('source');
  const t = E('manuscript');
  t.setSelectionRange(t.value.length, t.value.length);
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
  if (visualMode && tiptapBridge && tiptapBridge.insertMarkdown && tiptapBridge.insertMarkdown(snippet)) return;
  const t = E('manuscript');
  t.value = t.value.replace(/\s*$/, '') + '\n\n' + snippet + '\n';
  markDirty();
  if (visualMode) renderVisualBlocks();
  preview().catch(error => status(error.message, true));
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
  addVisualMarkdown('$$\n\n$$');
  setEditorMode('source');
  E('manuscript').focus();
};
setEditorMode('source');
