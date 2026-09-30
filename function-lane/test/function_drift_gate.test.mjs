import test from 'node:test';
import assert from 'node:assert/strict';
import {functionDriftGate} from '../core/function_drift_gate.mjs';

const good=(elapsed=10)=>({completed:true,elapsed,errors:[]});
const baseline={avgElapsed:10,errorRate:0};

test('baseline-compatible behavior stays active',()=>{
 const r=functionDriftGate({functionId:'f1',baseline,recentRuns:[good(10),good(12),good(9)]}).functionDrift;
 assert.equal(r.state,'baseline-compatible');
});

test('large slowdown triggers drift before hard failure',()=>{
 const r=functionDriftGate({functionId:'f1',baseline,recentRuns:[good(30),good(30),good(30)]}).functionDrift;
 assert.equal(r.state,'drift-detected');
 assert.ok(r.drift.includes('elapsed'));
});

test('rising error rate triggers drift',()=>{
 const r=functionDriftGate({functionId:'f1',baseline,recentRuns:[good(),{completed:true,elapsed:10,errors:['x']},good()]}).functionDrift;
 assert.ok(r.drift.includes('errors'));
});

test('drift routes function to requalification',()=>{
 const r=functionDriftGate({functionId:'f1',baseline,recentRuns:[good(40),good(40)]}).functionDrift;
 assert.equal(r.action,'send-to-requalification');
});

test('unfinished runs do not distort drift measurement',()=>{
 const r=functionDriftGate({functionId:'f1',baseline,recentRuns:[good(10),good(10),{completed:false,elapsed:999,errors:['x']}]}).functionDrift;
 assert.equal(r.measuredRuns,2);
 assert.equal(r.state,'baseline-compatible');
});
