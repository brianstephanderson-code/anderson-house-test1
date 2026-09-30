import test from 'node:test';
import assert from 'node:assert/strict';
import {workStealingGate} from '../core/work_stealing_gate.mjs';

test('free capable bee steals from busy queue',()=>{
 const r=workStealingGate({freeBees:[{id:'bee-1',capabilities:['search']}],queues:[{id:'time',jobs:[{id:'t1',requires:['search']}]}]}).workStealing;
 assert.equal(r.assignments[0].jobId,'t1');
});

test('bee cannot steal job beyond its capability',()=>{
 const r=workStealingGate({freeBees:[{id:'bee-1',capabilities:['search']}],queues:[{id:'verify',jobs:[{id:'v1',requires:['verification']}]}]}).workStealing;
 assert.equal(r.state,'no-safe-steal');
});

test('not-ready job cannot be stolen',()=>{
 const r=workStealingGate({freeBees:[{id:'bee-1',capabilities:['search']}],queues:[{id:'time',jobs:[{id:'t1',requires:['search'],ready:false}]}]}).workStealing;
 assert.equal(r.assignments.length,0);
});

test('busy queue is considered before smaller queue',()=>{
 const r=workStealingGate({freeBees:[{id:'bee-1',capabilities:['search']}],queues:[
  {id:'small',jobs:[{id:'s1',requires:['search']}]},
  {id:'large',jobs:[{id:'l1',requires:['search']},{id:'l2',requires:['search']}]}
 ]}).workStealing;
 assert.equal(r.assignments[0].fromQueue,'large');
});

test('multiple free bees can drain separate ready jobs',()=>{
 const r=workStealingGate({freeBees:[
  {id:'bee-1',capabilities:['search']},{id:'bee-2',capabilities:['search']}
 ],queues:[{id:'archive',jobs:[{id:'a1',requires:['search']},{id:'a2',requires:['search']}]}]}).workStealing;
 assert.equal(r.assignments.length,2);
});
