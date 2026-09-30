import test from 'node:test';
import assert from 'node:assert/strict';
import { humilityGate } from '../core/humility_gate.mjs';

const passport={state:'verified'};
const logic=['claim','evidence','context','verification'];

test('traceable finding can remain current DONE',()=>{
  const x=humilityGate({finding:'x',origin:'our-research',evidencePassport:passport,logicTrace:logic}).humilityGate;
  assert.equal(x.state,'current-done');
});

test('better test function reopens our own DONE',()=>{
  const x=humilityGate({finding:'x',origin:'our-research',evidencePassport:passport,logicTrace:logic,newTestFunction:true}).humilityGate;
  assert.equal(x.state,'reopen');
});

test('new contradictory evidence reopens DONE',()=>{
  const x=humilityGate({finding:'x',origin:'outside-glossary',evidencePassport:passport,logicTrace:logic,contradiction:true}).humilityGate;
  assert.equal(x.state,'reopen');
});

test('untraceable old answer gets recast rather than grandfathered',()=>{
  const x=humilityGate({finding:'x',origin:'our-old-answer'}).humilityGate;
  assert.equal(x.state,'recast');
});
