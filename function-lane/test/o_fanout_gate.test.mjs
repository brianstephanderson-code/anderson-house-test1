import test from 'node:test';
import assert from 'node:assert/strict';
import {oFanoutGate} from '../core/o_fanout_gate.mjs';

const hole={stateProvides:['raw-term','context'],doneRequires:['context-fit-definition']};

test('same hole fans out to many function universes',()=>{
 const r=oFanoutGate({hole,surveyDoors:[
  {id:'warehouse-bee',universe:'warehouse'},
  {id:'bridge-bee',universe:'external-proven-functions'},
  {id:'combo-bee',universe:'function-combinations'},
  {id:'capability-bee',universe:'worker-capabilities'},
  {id:'bypass-bee',universe:'alternate-routes'}
 ]}).oFanout;
 assert.equal(r.parallelCapacity,5);
 assert.ok(r.jobs.every(j=>j.hole===hole));
});

test('each survey job returns candidates under same contract',()=>{
 const r=oFanoutGate({hole,surveyDoors:[{id:'a',universe:'warehouse'}]}).oFanout;
 assert.equal(r.jobs[0].doneContract,'return-candidate-functions-with-provenance');
});

test('duplicate universe casts remain visible',()=>{
 const r=oFanoutGate({hole,surveyDoors:[{id:'a',universe:'warehouse'},{id:'b',universe:'warehouse'}]}).oFanout;
 assert.equal(r.duplicateUniverses,1);
});

test('empty survey opens more function universes',()=>{
 const r=oFanoutGate({hole,surveyDoors:[]}).oFanout;
 assert.equal(r.state,'open-more-function-universes');
});

test('candidate survey does not preselect a winning function',()=>{
 const r=oFanoutGate({hole,surveyDoors:[{id:'a',universe:'warehouse'},{id:'b',universe:'alternate-routes'}]}).oFanout;
 assert.equal('selectedFunction' in r,false);
});
