import test from 'node:test';
import assert from 'node:assert/strict';
import {functionRequalificationGate} from '../core/function_requalification_gate.mjs';

const good={completed:true,doneSatisfied:true,evidenceIntegrity:true,contextPreserved:true,errors:[]};
const bad={completed:true,doneSatisfied:false,evidenceIntegrity:true,contextPreserved:true,errors:['fail']};

test('quarantined function returns after required clean streak',()=>{
 const r=functionRequalificationGate({functionId:'f1',quarantined:true,retestRuns:[good,good,good],requiredCleanRuns:3}).functionRequalification;
 assert.equal(r.action,'restore-to-proven-pool');
});

test('too few clean retests keeps function quarantined',()=>{
 const r=functionRequalificationGate({functionId:'f1',quarantined:true,retestRuns:[good,good],requiredCleanRuns:3}).functionRequalification;
 assert.equal(r.action,'keep-quarantined');
});

test('recent failure resets recovery streak',()=>{
 const r=functionRequalificationGate({functionId:'f1',quarantined:true,retestRuns:[good,good,bad],requiredCleanRuns:3}).functionRequalification;
 assert.equal(r.cleanRecoveryStreak,0);
 assert.equal(r.action,'keep-quarantined');
});

test('old failure does not block later clean recovery streak',()=>{
 const r=functionRequalificationGate({functionId:'f1',quarantined:true,retestRuns:[bad,good,good,good],requiredCleanRuns:3}).functionRequalification;
 assert.equal(r.action,'restore-to-proven-pool');
});

test('active nonquarantined function is left to normal health gate',()=>{
 const r=functionRequalificationGate({functionId:'f1',quarantined:false,retestRuns:[good,good,good]}).functionRequalification;
 assert.equal(r.action,'not-quarantined');
});
