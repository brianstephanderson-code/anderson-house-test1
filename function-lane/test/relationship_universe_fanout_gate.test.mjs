import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipUniverseFanoutGate} from '../core/relationship_universe_fanout_gate.mjs';

const gap={left:'unknown-A',right:'unknown-B'};

test('same gap fans into many relationship universes',()=>{
 const r=relationshipUniverseFanoutGate({gap,universes:['semantic','phonetic','temporal','cultural']}).relationshipUniverseFanout;
 assert.equal(r.parallelCapacity,4);
 assert.ok(r.jobs.every(j=>j.gap===gap));
});

test('duplicate universes do not waste bees',()=>{
 const r=relationshipUniverseFanoutGate({gap,universes:['semantic','semantic','phonetic']}).relationshipUniverseFanout;
 assert.equal(r.parallelCapacity,2);
});

test('every universe returns under common provenance contract',()=>{
 const r=relationshipUniverseFanoutGate({gap,universes:['functional']}).relationshipUniverseFanout;
 assert.equal(r.jobs[0].doneContract,'return-candidate-bridges-with-provenance');
});

test('fanout does not preselect a winning universe',()=>{
 const r=relationshipUniverseFanoutGate({gap,universes:['semantic','phonetic']}).relationshipUniverseFanout;
 assert.equal(r.selection,null);
});

test('no known universes triggers universe discovery',()=>{
 const r=relationshipUniverseFanoutGate({gap,universes:[]}).relationshipUniverseFanout;
 assert.equal(r.state,'discover-more-relationship-universes');
});
