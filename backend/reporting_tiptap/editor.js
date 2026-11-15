/**
 * SC-PUB-TIPTAP-01 — Sustainable Catalyst Scientific Publication Studio.
 *
 * Production imports the MIT-licensed Tiptap 3 runtime through the local
 * Reporting Studio build. NO CDN, NO extra account, NO remote editor service.
 * The existing Markdown input, owner-scoped revision save, immutable source
 * hashes and HTML/PDF/DOCX export endpoints remain authoritative.
 *
 * Only a block the user explicitly edits is serialized from Tiptap. Equations,
 * figures, tables, code, complex Markdown and source-only syntax never pass
 * through the beta Markdown parser during passive viewing or saving.
 */
import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { Markdown } from '@tiptap/markdown';
import {
  splitMarkdown, joinMarkdown, classifyMarkdownBlock, replaceEditedBlock,
} from './source-bridge.js';

const editors = [];
let pendingPreview = null;
let sourceParts = [];
let sourcePrefix = '';
const e = id => document.getElementById(id);

function release() {
  if (pendingPreview) { clearTimeout(pendingPreview); pendingPreview = null; }
  for (const editor of editors.splice(0)) editor.destroy();
  e('visualBlocks').replaceChildren();
}

function syncEditedBlock(part, markdown) {
  part.raw = replaceEditedBlock(part.raw, markdown);
  e('manuscript').value = joinMarkdown(sourcePrefix, sourceParts);
  // Existing Workspace handlers invalidate export buttons until the revision
  // is saved, and still enforce optimistic concurrency in the backend.
  markDirty();
  if (pendingPreview) clearTimeout(pendingPreview);
  pendingPreview = setTimeout(
    () => preview().catch(error => status(error.message, true)), 650
  );
}

function formattingButton(editor, name, label, command, isActive) {
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'sc-rich-command'; b.textContent = label;
  b.setAttribute('aria-label', name);
  // Keep the editor selection while the toolbar button is clicked.
  b.addEventListener('mousedown', event => event.preventDefault());
  b.addEventListener('click', () => { command(); b.setAttribute('aria-pressed', String(isActive())); });
  b.setAttribute('aria-pressed', String(isActive()));
  return b;
}

function richBlock(part, kind, index) {
  const box = document.createElement('section');
  box.className = 'sc-block sc-tiptap-block';
  const label = document.createElement('div');
  label.className = 'sc-rich-label';
  label.textContent = {heading:'Heading',paragraph:'Paragraph',list:'List',quote:'Quotation'}[kind];
  const bar = document.createElement('div'); bar.className = 'sc-rich-toolbar';
  const mount = document.createElement('div'); mount.className = 'sc-rich-content';
  box.append(label,bar,mount);

  let editor;
  try {
    editor = new Editor({
      element: mount,
      extensions: [StarterKit, Markdown],
      content: part.raw,
      contentType: 'markdown',
      editorProps: {
        attributes: {
          'aria-label': 'Editable '+kind+' '+String(index + 1),
          'data-sc-research-editor': 'tiptap',
          spellcheck: 'true',
        },
      },
      onUpdate: ({editor: instance}) => {
        syncEditedBlock(part, instance.getMarkdown());
      },
    });
  } catch (error) {
    // Fail closed for this block. Do not ever drop or mutate original source.
    const preserved = document.createElement('pre');
    preserved.textContent = part.raw;
    const message = document.createElement('p');
    message.className = 'preserved';
    message.textContent = 'Visual conversion unavailable. Original source preserved; use Markdown mode.';
    box.replaceChildren(label,preserved,message);
    return box;
  }
  editors.push(editor);
  bar.append(
    formattingButton(editor, 'Bold', 'B',
      () => editor.chain().focus().toggleBold().run(), () => editor.isActive('bold')),
    formattingButton(editor, 'Italic', 'I',
      () => editor.chain().focus().toggleItalic().run(), () => editor.isActive('italic')),
    formattingButton(editor, 'Heading 2', 'H2',
      () => editor.chain().focus().toggleHeading({level:2}).run(), () => editor.isActive('heading',{level:2})),
    formattingButton(editor, 'Bulleted list', 'List',
      () => editor.chain().focus().toggleBulletList().run(), () => editor.isActive('bulletList')),
    formattingButton(editor, 'Undo', 'Undo',
      () => editor.chain().focus().undo().run(), () => false),
    formattingButton(editor, 'Redo', 'Redo',
      () => editor.chain().focus().redo().run(), () => false),
  );
  return box;
}

function sourceOnlyBlock(raw) {
  const box = document.createElement('section');
  box.className = 'sc-block technical sc-source-only';
  const label = document.createElement('div');
  label.className = 'sc-rich-label';
  label.textContent = 'Preserved scientific source';
  const note = document.createElement('p');
  note.className = 'preserved';
  note.textContent = 'Equation, table, figure, code or complex Markdown. Original bytes remain untouched.';
  const pre = document.createElement('pre'); pre.textContent = raw;
  const button = document.createElement('button'); button.type='button';
  button.textContent='Edit in Markdown';
  button.addEventListener('click', () => {
    setEditorMode('source'); e('manuscript').focus();
  });
  box.append(label,note,pre,button);
  return box;
}

function render() {
  release();
  const source = e('manuscript').value;
  const parsed = splitMarkdown(source);
  sourceParts = parsed.parts;
  sourcePrefix = parsed.prefix;
  const container = e('visualBlocks');
  // Avoid thousands of ProseMirror instances in an unexpectedly large file.
  // Source mode stays available without losing the original document.
  if (sourceParts.length > 120) {
    const note = document.createElement('p'); note.className='preserved';
    note.textContent = 'This manuscript exceeds the 120-block visual-editing limit. Use Markdown source until sections are split.';
    container.append(note);
    return;
  }
  if (!sourceParts.length) {
    const note = document.createElement('p'); note.className='hint';
    note.textContent = 'Create a new report section to start editing.';
    container.append(note);
  }
  for (const [index, part] of sourceParts.entries()) {
    const kind = classifyMarkdownBlock(part.raw);
    container.append(kind === 'protected' ? sourceOnlyBlock(part.raw) : richBlock(part,kind,index));
  }
}

if (!window.SCStudioRegisterTiptap) {
  throw Error('Sustainable Catalyst Publication Studio host is not loaded');
}
window.SCStudioRegisterTiptap({render,destroy:release});
