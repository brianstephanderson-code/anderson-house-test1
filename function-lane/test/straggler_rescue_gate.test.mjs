import test from 'node:test';
import assert from 'node:assert/strict';
import {stragglerRescueGate} from '../core/straggler_rescue_gate.mjs';

const now=100000;

test('slow required job is rescued',()=>{
 const r=stragglerRescueGate({now,rescueAfterMs:1000,jobs:[{id:'time-1',state:'working',startedAt:98000,requiredForJoin:true}]}).stragglerRescue;
 assert.equal(r.state,'rescue-stragglers');
 assert.equal(r.rescue[0].jobId,'time-1');
});

test('healthy required job is left alone',()=>{
 const r=stragglerRescueGate({now,rescueAfterMs:5000,jobs:[{id:'time-1',state:'working',startedAt:98000,requiredForJoin:true}]}).stragglerRescue;
 assert.equal(r.state,'no-rescue-needed');
});

test('slow unrelated job does not trigger join rescue',()=>{
 const r=stragglerRescueGate({now,rescueAfterMs:1000,jobs:[{id:'extra-1',state:'working',startedAt:90000,requiredForJoin:false}]}).stragglerRescue;
 assert.equal(r.rescue.length,0);
});

test('completed job is never duplicated',()=>{
 const r=stragglerRescueGate({now,rescueAfterMs:1000,jobs:[{id:'time-1',state:'done',startedAt:90000,requiredForJoin:true}]}).stragglerRescue;
 assert.equal(r.rescue.length,0);
});

test('duplicate completion policy is first valid return wins',()=>{
 const r=stragglerRescueGate({now,jobs:[]}).stragglerRescue;
 assert.equal(r.completionRule,'first-valid-return-wins');
 assert.equal(r.duplicateRule,'late-duplicate-close-without-double-counting');
});
