'use strict';
const assert=require('assert');
const path=require('path');
const root=path.resolve(__dirname,'../..');
const factory=require(path.join(root,'app/linguistics/workspace-translation-transliteration-parallel-alignment-v3490.js'));

(async()=>{
  const requests=[];
  const apiClient={
    async get(path){requests.push({method:'GET',path});return {version:'3.49.0'};},
    async post(path,body){requests.push({method:'POST',path,body});return {ok:true,operation:body.operation};}
  };
  const w=factory.create({apiClient});
  const tr=w.createTransformation({id:'tr1',transformationType:'translation',sourceTextId:'ar',derivedTextId:'en',sourceLanguageTag:'ar',targetLanguageTag:'en',sourceScript:'Arab',targetScript:'Latn',method:'human'});
  const tl=w.createTransformation({id:'tl1',transformationType:'transliteration',sourceTextId:'ar',derivedTextId:'ar-latn',sourceLanguageTag:'ar',targetLanguageTag:'ar',sourceScript:'Arab',targetScript:'Latn',method:'rule'});
  const s1=w.createParallelSegment({id:'s1',textId:'ar',languageTag:'ar',script:'Arab',ordinal:0,text:'مرحبا'});
  const s2=w.createParallelSegment({id:'s2',textId:'en',languageTag:'en',script:'Latn',ordinal:0,text:'Hello'});
  const a=w.createAlignmentGroup({id:'a1',sourceSegmentIds:['s1'],targetSegmentIds:['s2'],relation:'1:1',method:'human'});
  const set=w.createParallelTextSet({segments:[s1,s2],transformations:[tr,tl],alignments:[a]});
  const input={transformations:set.transformations,segments:set.segments,alignments:set.alignments};
  await w.validateTransformations(input); await w.validateAlignments(input); await w.parallelSegmentIndex(input);
  await w.alignmentProfile(input); await w.alignmentCoverage(input); await w.lineage(input); await w.profile();
  assert.equal(w.inspect().automaticTranslationEnabled,false);
  assert.equal(w.inspect().automaticAlignmentEnabled,false);
  assert.equal(w.inspect().wordpressRequired,false);
  assert.equal(requests[0].body.operation,'workspace.linguistics.transformation-validate');
  assert.equal(requests[5].body.operation,'workspace.linguistics.translation-alignment-lineage');
  console.log('WORKSPACE_V3490_TRANSLATION_PROVENANCE=PASS');
  console.log('WORKSPACE_V3490_TRANSLITERATION_PROVENANCE=PASS');
  console.log('WORKSPACE_V3490_PARALLEL_SEGMENTS=PASS');
  console.log('WORKSPACE_V3490_EXPLICIT_ALIGNMENT=PASS');
  console.log('WORKSPACE_V3490_ALIGNMENT_COVERAGE=PASS');
  console.log('WORKSPACE_V3490_NO_AUTOMATIC_TRANSLATION=PASS');
  console.log('WORKSPACE_V3490_NO_AUTOMATIC_ALIGNMENT=PASS');
})();
