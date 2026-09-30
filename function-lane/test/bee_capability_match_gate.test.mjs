import test from 'node:test';
import assert from 'node:assert/strict';
import {beeCapabilityMatchGate} from '../core/bee_capability_match_gate.mjs';

const job={id:'period-check',requires:['search','period-fit']};

test('any free capable bee may take the job',()=>{
 const r=beeCapabilityMatchGate({job,bees:[
  {id:'bee-1',state:'busy',capabilities:['search','period-fit']},
  {id:'bee-2',state:'free',capabilities:['search','period-fit']}
 ]}).beeCapabilityMatch;
 assert.equal(r.selected,'bee-2');
});

test('missing capability blocks assignment',()=>{
 const r=beeCapabilityMatchGate({job,bees:[{id:'bee-1',state:'free',capabilities:['search']}]}).beeCapabilityMatch;
 assert.equal(r.state,'no-capable-free-bee');
});

test('busy capable bee is not assigned',()=>{
 const r=beeCapabilityMatchGate({job,bees:[{id:'bee-1',state:'busy',capabilities:['search','period-fit']}]}).beeCapabilityMatch;
 assert.equal(r.selected,null);
});

test('lower-load eligible bee is selected first',()=>{
 const r=beeCapabilityMatchGate({job,bees:[
  {id:'bee-A',state:'free',capabilities:['search','period-fit'],load:3},
  {id:'bee-B',state:'free',capabilities:['search','period-fit'],load:0}
 ]}).beeCapabilityMatch;
 assert.equal(r.selected,'bee-B');
});

test('worker identity is irrelevant when capabilities match',()=>{
 const r=beeCapabilityMatchGate({job,bees:[
  {id:'cloud-bee',state:'free',capabilities:['search','period-fit']},
  {id:'chat-bee',state:'free',capabilities:['search','period-fit']}
 ]}).beeCapabilityMatch;
 assert.equal(r.eligible.length,2);
});
