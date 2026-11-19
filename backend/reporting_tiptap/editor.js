/**
 * SC-PUB-TIPTAP-01 / SC-EDITOR-DOCX-01 — Sustainable Catalyst Scientific Publication Studio.
 *
 * Production imports the MIT-licensed Tiptap 3 runtime through the local
 * Reporting Studio build. NO CDN, NO extra account, NO remote editor service.
 * The existing Markdown input, owner-scoped revision save, immutable source
 * hashes and HTML/PDF/DOCX export endpoints remain authoritative.
 *
 * One continuous manuscript editor with one shared toolbar and an outline.
 * Every top-level node remembers the source block it came from. On save, a
 * block whose serialization is unchanged is written back byte for byte; only
 * blocks the researcher actually edited are re-serialized. Equations, figures,
 * code and complex Markdown are atom nodes that carry their original source
 * and never pass through the beta Markdown parser.
 */
import { Editor, Extension, Node, mergeAttributes } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { Markdown } from '@tiptap/markdown';
import { TableKit } from '@tiptap/extension-table';
import { Plugin, PluginKey } from '@tiptap/pm/state';
import { Decoration, DecorationSet } from '@tiptap/pm/view';
import {
  splitMarkdown, classifyMarkdownBlock, replaceEditedBlock, restoreCitationMarkers,
} from './source-bridge.js';

const PART_TYPES = ['paragraph', 'heading', 'bulletList', 'orderedList', 'blockquote', 'table',
  'codeBlock', 'horizontalRule'];
const FIGURE = /^!\[([^\]]{0,160})\]\(asset:([A-Za-z0-9_.-]{1,160})\)$/;
const CITATION = /\[@([A-Za-z0-9_.:-]{1,80})(?:,[^;\]\n]{1,40})?(?:;\s*@[A-Za-z0-9_.:-]{1,80}(?:,[^;\]\n]{1,40})?)*\]/g;
const REFERENCES = /^(?:list of )?(?:references?|reference list|bibliography|works cited|literature cited|sources cited):?$/i;
const MAX_PARTS = 3000;

let editor = null;
let shell = null;
let sourceParts = [];
let sourcePrefix = '';
let baseline = [];
let inserted = new Set();
let pendingPreview = null;
let pendingOutline = null;
let citationVersion = 0;
const e = id => document.getElementById(id);
const el = (tag, props = {}, ...children) => {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
};

// Each top-level block remembers the source part it came from (never rendered).
const SourceParts = Extension.create({
  name: 'scSourceParts',
  addGlobalAttributes() {
    return [{types: PART_TYPES, attributes: {scPart: {default: null, rendered: false, keepOnSplit: true}}}];
  },
});

// Protected scientific source: shown in place, carried byte for byte.
const ScientificSource = Node.create({
  name: 'scSource',
  group: 'block',
  atom: true,
  selectable: true,
  draggable: false,
  addAttributes() {
    return {raw: {default: ''}, kind: {default: 'source'}, assetId: {default: null},
      caption: {default: ''}, scPart: {default: null}};
  },
  parseHTML() { return [{tag: 'div[data-sc-source]'}]; },
  renderHTML() { return ['div', mergeAttributes({'data-sc-source': ''})]; },
  renderMarkdown(node) { return String(node.attrs.raw).replace(/\n+$/, ''); },
  addNodeView() {
    return ({node}) => {
      let dom;
      if (node.attrs.kind === 'figure') {
        const url = window.SCStudioAssetUrl ? window.SCStudioAssetUrl(node.attrs.assetId) : '';
        const img = el('img', {alt: node.attrs.caption, loading: 'lazy'});
        if (url) img.src = url;
        dom = el('figure', {className: 'sc-doc-figure', contentEditable: 'false'},
          img, el('figcaption', {textContent: node.attrs.caption}));
        dom.dataset.assetId = node.attrs.assetId;
      } else {
        const button = el('button', {type: 'button', textContent: 'Edit in Markdown'});
        button.addEventListener('click', () => { setEditorMode('source'); e('manuscript').focus(); });
        dom = el('div', {className: 'sc-doc-source', contentEditable: 'false'},
          el('span', {className: 'sc-rich-label', textContent: 'Preserved scientific source'}),
          el('pre', {textContent: node.attrs.raw.replace(/\n+$/, '')}), button);
      }
      return {dom, ignoreMutation: () => true};
    };
  },
});

// Linked in-text citations and the hanging-indent reference list.
const Scholarly = Extension.create({
  name: 'scScholarly',
  addProseMirrorPlugins() {
    let lastDoc = null, lastVersion = -1, lastSet = DecorationSet.empty;
    return [new Plugin({
      key: new PluginKey('scScholarly'),
      props: {
        decorations(state) {
          if (state.doc === lastDoc && citationVersion === lastVersion) return lastSet;
          const decorations = [];
          let level = null;
          state.doc.forEach((node, offset) => {
            if (node.type.name === 'heading') {
              if (REFERENCES.test(node.textContent.trim())) level = node.attrs.level;
              else if (level !== null && node.attrs.level <= level) level = null;
            } else if (node.type.name === 'paragraph' && level !== null) {
              decorations.push(Decoration.node(offset, offset + node.nodeSize, {class: 'sc-ref-entry'}));
            }
          });
          state.doc.descendants((node, pos) => {
            if (!node.isText) return;
            for (const match of node.text.matchAll(CITATION)) {
              const label = window.SCStudioCitationLabel ? window.SCStudioCitationLabel(match[1]) : '';
              decorations.push(Decoration.inline(pos + match.index, pos + match.index + match[0].length,
                {class: label ? 'sc-cite' : 'sc-cite unresolved', title: label || 'Not in this project’s citations'}));
            }
          });
          lastDoc = state.doc;
          lastVersion = citationVersion;
          lastSet = DecorationSet.create(state.doc, decorations);
          return lastSet;
        },
      },
    })];
  },
});

function serialize(nodes) {
  const content = nodes.map(node => ({...node, attrs: {...(node.attrs || {}), scPart: null}}));
  return editor.markdown.serialize({type: 'doc', content}).replace(/\n+$/, '');
}

// Source parts -> one document. Unsupported structures become protected atoms.
function documentFor(source) {
  const {prefix, parts} = splitMarkdown(source);
  sourcePrefix = prefix; sourceParts = parts;
  const content = [];
  parts.forEach((part, index) => {
    const kind = classifyMarkdownBlock(part.raw);
    if (kind !== 'protected') {
      try {
        const nodes = (editor.markdown.parse(part.raw).content || []);
        if (nodes.length && nodes.every(n => PART_TYPES.includes(n.type))) {
          for (const node of nodes) content.push({...node, attrs: {...(node.attrs || {}), scPart: index}});
          return;
        }
      } catch (error) { /* fall through: keep the block as preserved source */ }
    }
    const figure = part.raw.trim().match(FIGURE);
    content.push({type: 'scSource', attrs: {raw: part.raw, kind: figure ? 'figure' : 'source',
      assetId: figure ? figure[2] : null, caption: figure ? figure[1] : '', scPart: index}});
  });
  return {type: 'doc', content: content.length ? content : [{type: 'paragraph'}]};
}

function groups() {
  const out = [];
  for (const node of editor.getJSON().content || []) {
    const key = node.attrs && node.attrs.scPart != null ? node.attrs.scPart : null;
    const last = out[out.length - 1];
    if (last && key !== null && last.key === key) last.nodes.push(node);
    else out.push({key, nodes: [node]});
  }
  return out;
}

// The document -> Markdown. Untouched blocks keep their exact source bytes.
export function currentMarkdown() {
  let out = sourcePrefix;
  const used = new Set();
  for (const group of groups()) {
    const part = group.key !== null && !used.has(group.key) ? sourceParts[group.key] : null;
    if (part) used.add(group.key);
    let text;
    if (group.nodes.length === 1 && group.nodes[0].type === 'scSource') {
      text = part ? part.raw : group.nodes[0].attrs.raw.replace(/\n*$/, '\n');
    } else {
      const markdown = serialize(group.nodes);
      if (!markdown.trim()) continue;
      if (part && markdown === baseline[group.key]) text = part.raw;
      else {
        const restored = restoreCitationMarkers(markdown, part ? part.raw : '', [...inserted]);
        text = part ? replaceEditedBlock(part.raw, restored) : restored + '\n';
        if (!/\n$/.test(text)) text += '\n';
      }
    }
    if (out.length > sourcePrefix.length && !/\n\n$/.test(out)) out = out.replace(/\n*$/, '\n\n');
    out += text + (part ? part.separator : '\n');
  }
  return out;
}

function sync() {
  e('manuscript').value = currentMarkdown();
  markDirty();
  if (pendingPreview) clearTimeout(pendingPreview);
  pendingPreview = setTimeout(() => preview().catch(error => status(error.message, true)), 650);
  scheduleOutline();
}

// Shared toolbar --------------------------------------------------------------------------------------------
function command(label, name, run, active) {
  const button = el('button', {type: 'button', className: 'sc-rich-command', textContent: label});
  button.setAttribute('aria-label', name);
  button.title = name;
  button.addEventListener('mousedown', event => event.preventDefault());  // keep the selection
  button.addEventListener('click', () => { run(); refreshToolbar(); });
  button._active = active;
  return button;
}

function refreshToolbar() {
  if (!shell || !editor) return;
  for (const button of shell.toolbar.querySelectorAll('button')) {
    if (button._active) button.setAttribute('aria-pressed', String(Boolean(button._active())));
  }
  const block = shell.blockType;
  block.value = editor.isActive('heading', {level: 1}) ? 'h1' : editor.isActive('heading', {level: 2}) ? 'h2'
    : editor.isActive('heading', {level: 3}) ? 'h3' : editor.isActive('heading', {level: 4}) ? 'h4' : 'p';
  const inTable = editor.isActive('table');
  for (const button of shell.tableCommands) button.disabled = !inTable;
}

function citationOptions() {
  const select = shell.cite;
  const items = window.SCStudioCitations ? window.SCStudioCitations() : [];
  select.replaceChildren(el('option', {value: '', textContent: items.length ? 'Cite…' : 'Cite (no project citations)'}));
  for (const item of items) select.append(el('option', {value: item.key, textContent: item.label}));
}

export function insertCitation(key) {
  if (!editor || !/^[A-Za-z0-9_.:-]{1,80}$/.test(key)) return false;
  const marker = '[@' + key + ']';
  inserted.add(marker);
  const {from} = editor.state.selection;
  const before = from > 1 ? editor.state.doc.textBetween(from - 1, from, '\n', '\n') : '';
  editor.chain().focus().insertContent({type: 'text', text: (before && !/\s/.test(before) ? ' ' : '') + marker}).run();
  return true;
}

function buildToolbar() {
  const toolbar = el('div', {className: 'sc-doc-toolbar', role: 'toolbar'});
  toolbar.setAttribute('aria-label', 'Manuscript formatting');
  const blockType = el('select', {className: 'sc-block-type'});
  blockType.setAttribute('aria-label', 'Paragraph style');
  for (const [value, label] of [['p', 'Paragraph'], ['h1', 'Title / Heading 1'], ['h2', 'Heading 2'],
    ['h3', 'Heading 3'], ['h4', 'Heading 4']]) blockType.append(el('option', {value, textContent: label}));
  blockType.addEventListener('change', () => {
    const chain = editor.chain().focus();
    if (blockType.value === 'p') chain.setParagraph().run();
    else chain.setHeading({level: Number(blockType.value[1])}).run();
  });
  const linkInput = el('input', {type: 'url', placeholder: 'https://…', className: 'sc-link-input'});
  linkInput.setAttribute('aria-label', 'Link address');
  const tableCommands = [
    command('+Row', 'Add table row', () => editor.chain().focus().addRowAfter().run()),
    command('+Col', 'Add table column', () => editor.chain().focus().addColumnAfter().run()),
    command('−Row', 'Delete table row', () => editor.chain().focus().deleteRow().run()),
    command('−Col', 'Delete table column', () => editor.chain().focus().deleteColumn().run()),
  ];
  const cite = el('select', {className: 'sc-cite-select'});
  cite.setAttribute('aria-label', 'Insert citation');
  cite.addEventListener('change', () => {
    if (cite.value && insertCitation(cite.value)) status('Citation [@' + cite.value + '] inserted at the cursor.');
    cite.value = '';
  });
  toolbar.append(
    blockType,
    command('B', 'Bold', () => editor.chain().focus().toggleBold().run(), () => editor.isActive('bold')),
    command('I', 'Italic', () => editor.chain().focus().toggleItalic().run(), () => editor.isActive('italic')),
    linkInput,
    command('Link', 'Apply link to selection', () => {
      const url = linkInput.value.trim();
      if (!url) editor.chain().focus().unsetLink().run();
      else if (/^(https?:\/\/|mailto:)/i.test(url)) editor.chain().focus().setLink({href: url}).run();
      else status('Links must start with https://, http:// or mailto:', true);
    }, () => editor.isActive('link')),
    command('• List', 'Bulleted list', () => editor.chain().focus().toggleBulletList().run(), () => editor.isActive('bulletList')),
    command('1. List', 'Numbered list', () => editor.chain().focus().toggleOrderedList().run(), () => editor.isActive('orderedList')),
    command('“ Quote', 'Block quotation', () => editor.chain().focus().toggleBlockquote().run(), () => editor.isActive('blockquote')),
    command('Table', 'Insert table', () => editor.chain().focus().insertTable({rows: 3, cols: 3, withHeaderRow: true}).run()),
    ...tableCommands,
    cite,
    command('Undo', 'Undo', () => editor.chain().focus().undo().run()),
    command('Redo', 'Redo', () => editor.chain().focus().redo().run()),
  );
  return {toolbar, blockType, tableCommands, cite, linkInput};
}

// Outline ---------------------------------------------------------------------------------------------------
function scheduleOutline() {
  if (pendingOutline) clearTimeout(pendingOutline);
  pendingOutline = setTimeout(renderOutline, 250);
}

function renderOutline() {
  if (!shell || !editor) return;
  const list = el('ol', {className: 'sc-outline-list'});
  editor.state.doc.forEach((node, offset) => {
    if (node.type.name !== 'heading' || !node.textContent.trim()) return;
    const button = el('button', {type: 'button', textContent: node.textContent});
    button.className = 'sc-outline-h' + node.attrs.level;
    button.addEventListener('click', () => {
      editor.chain().focus().setTextSelection(offset + 1).scrollIntoView().run();
      const dom = editor.view.nodeDOM(offset);
      if (dom && dom.scrollIntoView) dom.scrollIntoView({block: 'start', behavior: 'smooth'});
    });
    list.append(el('li', {}, button));
  });
  shell.outline.replaceChildren(el('strong', {textContent: 'Outline'}), list);
}

// Lifecycle -------------------------------------------------------------------------------------------------
function release() {
  if (pendingPreview) { clearTimeout(pendingPreview); pendingPreview = null; }
  if (pendingOutline) { clearTimeout(pendingOutline); pendingOutline = null; }
  if (editor) { editor.destroy(); editor = null; }
  shell = null;
  e('visualBlocks').replaceChildren();
}

function render() {
  release();
  const container = e('visualBlocks');
  const source = e('manuscript').value;
  if ((source.match(/\n\s*\n/g) || []).length > MAX_PARTS) {
    container.append(el('p', {className: 'preserved',
      textContent: 'This manuscript exceeds the visual-editing limit. Use Markdown source until sections are split.'}));
    return;
  }
  const bar = buildToolbar();
  const outline = el('nav', {className: 'sc-doc-outline'});
  outline.setAttribute('aria-label', 'Document outline');
  const page = el('div', {className: 'sc-doc-page'});
  container.append(bar.toolbar, el('div', {className: 'sc-doc-shell'}, outline, page));
  shell = {...bar, outline, page};
  inserted = new Set();
  try {
    editor = new Editor({
      element: page,
      extensions: [StarterKit.configure({link: {openOnClick: false, autolink: false}}), Markdown,
        TableKit.configure({table: {resizable: false}}), SourceParts, ScientificSource, Scholarly],
      editorProps: {attributes: {'aria-label': 'Manuscript', 'data-sc-research-editor': 'tiptap', spellcheck: 'true'}},
    });
    editor.commands.setContent(documentFor(source), {emitUpdate: false});
    baseline = [];
    for (const group of groups()) {
      if (group.key !== null && !(group.nodes.length === 1 && group.nodes[0].type === 'scSource')) {
        baseline[group.key] = serialize(group.nodes);
      }
    }
    // A pristine load must reproduce the saved manuscript exactly.
    if (currentMarkdown() !== source) throw Error('Visual round trip differs from the saved source');
  } catch (error) {
    release();
    container.append(el('p', {className: 'preserved',
      textContent: 'Visual editing is unavailable for this manuscript (' + error.message + '). Original source preserved; use Markdown mode.'}));
    console.error(error);
    return;
  }
  editor.on('update', sync);
  editor.on('selectionUpdate', refreshToolbar);
  editor.on('transaction', refreshToolbar);
  citationOptions();
  renderOutline();
  refreshToolbar();
}

function insertMarkdown(snippet) {
  if (!editor) return false;
  const nodes = editor.markdown.parse(snippet).content || [];
  editor.chain().focus().insertContent(nodes).run();
  return true;
}

function refreshCitations() {
  if (!editor) return;
  citationOptions();
  citationVersion += 1;
  editor.view.dispatch(editor.state.tr.setMeta('scCitations', true));
}

if (!window.SCStudioRegisterTiptap) {
  throw Error('Sustainable Catalyst Publication Studio host is not loaded');
}
window.SCStudioRegisterTiptap({render, destroy: release, insertCitation, insertMarkdown, refreshCitations,
  markdown: () => (editor ? currentMarkdown() : null)});
