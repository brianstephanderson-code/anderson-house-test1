import test from 'node:test';
import assert from 'node:assert/strict';
import { lineageGate } from '../core/lineage_gate.mjs';

const complete={finding:'reader explanation',sourceTextRef:'sleepy-hollow:p1:s2',evidenceIds:['ev-1'],marriageRefs:['mar-1'],handoffRefs:['hand-1'],decisionRefs:['verify-1'],rejectedAlternatives:['candidate-X'],uncertainty:'exact etymology unresolved'};

test('complete lineage is traceable',()=>{
  assert.equal(lineageGate(complete).lineage.state,'traceable');
});

test('missing original text reference returns parcel',()=>{
  const r=lineageGate({...complete,sourceTextRef:''}).lineage;
  assert.equal(r.state,'return');
  assert.ok(r.missing.includes('sourceTextRef'));
});

test('missing evidence marriage returns parcel',()=>{
  const r=lineageGate({...complete,marriageRefs:[]}).lineage;
  assert.equal(r.state,'return');
});

test('rejected alternatives and uncertainty survive trace',()=>{
  const r=lineageGate(complete).lineage;
  assert.deepEqual(r.rejectedAlternatives,['candidate-X']);
  assert.equal(r.uncertainty,'exact etymology unresolved');
});
