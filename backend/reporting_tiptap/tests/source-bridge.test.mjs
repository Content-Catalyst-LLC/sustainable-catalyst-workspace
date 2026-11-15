import { test } from 'node:test';
import assert from 'node:assert/strict';
import {splitMarkdown,joinMarkdown,classifyMarkdownBlock,replaceEditedBlock,restoreCitationMarkers} from '../source-bridge.js';

const wexford = [
 '# Wexford Enhanced Rock Weathering',
 '',
 'Additionality is evaluated against a baseline [@Beerling2020] and measured uncertainty.',
 '',
 '## Methods',
 '',
 '$$',
 'CO_2 + basalt \\rightarrow bicarbonate',
 '$$',
 '',
 '![Pinned experimental figure](asset:fig-01)',
 '',
 '| Parameter | Unit |',
 '|---|---|',
 '| Removal | t CO₂ |',
 '',
 '~~~python',
 'print("scientific source must not be rewritten")',
 '~~~',
 '',
 'A final paragraph with **emphasis** and [@Clarkson2024].',
 '',
].join('\n');

test('untouched report markdown reconstructs byte for byte', () => {
 const data=splitMarkdown(wexford);
 assert.equal(joinMarkdown(data.prefix,data.parts),wexford);
 assert.ok(data.parts.length>=6);
});

test('mathematics, code, pinned figures, tables remain protected',()=>{
 const {parts}=splitMarkdown(wexford);
 for (const part of parts) {
  if (/^\$\$|^!|^\||^~{3}/.test(part.raw.trimStart())) {
   assert.equal(classifyMarkdownBlock(part.raw),'protected',part.raw);
  }
 }
});

test('simple headings and paragraphs can be rich edited, citations stay in original source',()=>{
 const {parts}=splitMarkdown(wexford);
 assert.equal(classifyMarkdownBlock(parts[0].raw),'heading');
 assert.equal(classifyMarkdownBlock(parts[1].raw),'paragraph');
 assert.match(parts[1].raw,/\[@Beerling2020\]/);
});

test('editing one text block cannot rewrite neighboring source islands',()=>{
 const data=splitMarkdown(wexford);
 const before=data.parts.map(x=>x.raw);
 data.parts[1].raw=replaceEditedBlock(data.parts[1].raw,
   'The **updated** results reference [@Beerling2020].');
 const after=joinMarkdown(data.prefix,data.parts);
 assert.match(after,/\*\*updated\*\*/);
 assert.equal(data.parts[0].raw,before[0]);
 for (let i=2;i<data.parts.length;i++)assert.equal(data.parts[i].raw,before[i]);
 assert.match(after,/print\("scientific source must not be rewritten"\)/);
 assert.match(after,/!\[Pinned experimental figure\]\(asset:fig-01\)/);
});

test('nested content and embedded HTML require source mode',()=>{
 for (const s of [
  '<img onerror="alert(1)" src=x>',
  '| a | b |\n|---|---|\n| 1 | 2 |',
  '### Nested heading',
  '- [x] Approved',
  '$E=mc^2$',
 ])assert.equal(classifyMarkdownBlock(s),'protected',s);
});

test('newline convention and empty file survive',()=>{
 const empty=splitMarkdown('');
 assert.equal(joinMarkdown(empty.prefix,empty.parts),'');
 assert.equal(replaceEditedBlock('# One\n','## Two'),'## Two\n');
 const x=splitMarkdown('\n\n# A\n\n');
 assert.equal(joinMarkdown(x.prefix,x.parts),'\n\n# A\n\n');
});


test('Tiptap serializer escapes brackets but Citation Studio markers remain unchanged',()=>{
 const serialized='A result \\[@Beerling2020\\] and \\[@Clarkson2024\\].';
 assert.equal(restoreCitationMarkers(serialized),
   'A result [@Beerling2020] and [@Clarkson2024].');
 assert.equal(restoreCitationMarkers('\\[ordinary\\] and [@already]'),
   '\\[ordinary\\] and [@already]');
});
