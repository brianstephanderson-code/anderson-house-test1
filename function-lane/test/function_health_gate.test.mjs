import test from 'node:test';
import assert from 'node:assert/strict';
import {functionHealthGate} from '../core/function_health_gate.mjs';

const good={completed:true,doneSatisfied:true,evidenceIntegrity:true,contextPreserved:true,errors:[]};
const bad={completed:true,doneSatisfied:false,evidenceIntegrity:true,contextPreserved:true,errors:['failed']};

test('healthy proven function remains active',()=>{
 const r=functionHealthGate({functionId:'f1',recentRuns:[good,good,good],maxFailureRate:.2}).functionHealth;
 assert.equal(r.state,'healthy');
});

test('degraded function is removed from active routing pool',()=>{
 const r=functionHealthGate({functionId:'f1',recentRuns:[good,bad,bad],maxFailureRate:.2}).functionHealth;
 assert.equal(r.state,'degraded');
 assert.equal(r.routingAction,'remove-from-active-pool');
});

test('too little history does not pretend certainty',()=>{
 const r=functionHealthGate({functionId:'f1',recentRuns:[good],minRuns:3}).functionHealth;
 assert.equal(r.state,'insufficient-history');
});

test('context damage counts as failure',()=>{
 const r=functionHealthGate({functionId:'f1',recentRuns:[good,good,{...good,contextPreserved:false}],maxFailureRate:.2}).functionHealth;
 assert.equal(r.state,'degraded');
});

test('unfinished runs do not distort completed-run failure rate',()=>{
 const r=functionHealthGate({functionId:'f1',recentRuns:[good,good,good,{completed:false,doneSatisfied:false}],maxFailureRate:.2}).functionHealth;
 assert.equal(r.measuredRuns,3);
 assert.equal(r.failureRate,0);
});
