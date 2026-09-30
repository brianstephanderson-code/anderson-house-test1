import test from 'node:test';
import assert from 'node:assert/strict';
import {capabilityGapGate} from '../core/capability_gap_gate.mjs';

const job={id:'j1',requires:['search','archive-read']};

test('capable bee is recognized without modification',()=>{
 const r=capabilityGapGate({job,bees:[{id:'b1',capabilities:['search','archive-read'],state:'free'}]}).capabilityGap;
 assert.equal(r.state,'capability-present');
 assert.deepEqual(r.capableBees,['b1']);
});

test('missing worker skill opens capability O-gate',()=>{
 const r=capabilityGapGate({job,bees:[{id:'b1',capabilities:['search'],state:'free'}]}).capabilityGap;
 assert.equal(r.state,'open-capability-o-gate');
 assert.deepEqual(r.missingUniverse,['archive-read']);
});

test('gap is measured against function requirements, not worker identity',()=>{
 const r=capabilityGapGate({job,bees:[{id:'chat-bee',capabilities:['search']},{id:'cloud-bee',capabilities:['archive-read']}]}).capabilityGap;
 assert.equal(r.capableBees.length,0);
 assert.ok(r.analyses.every(x=>x.missing.length===1));
});

test('repair menu includes tool attachment and training',()=>{
 const r=capabilityGapGate({job,bees:[]}).capabilityGap;
 assert.ok(r.candidateRepairs.includes('attach-approved-tool'));
 assert.ok(r.candidateRepairs.includes('train-and-test-capability'));
});

test('empty workforce still describes required capability hole',()=>{
 const r=capabilityGapGate({job,bees:[]}).capabilityGap;
 assert.deepEqual(r.required,['search','archive-read']);
 assert.equal(r.state,'open-capability-o-gate');
});
