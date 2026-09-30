import test from 'node:test';
import assert from 'node:assert/strict';
import {capabilityRequalificationGate} from '../core/capability_requalification_gate.mjs';

const good={completed:true,capability:'archive-read',doneSatisfied:true,evidenceIntegrity:true,contextPreserved:true,errors:[]};
const bad={...good,doneSatisfied:false,errors:['fail']};

test('suspended capability returns after clean recovery streak',()=>{
 const r=capabilityRequalificationGate({beeId:'b1',capability:'archive-read',suspended:true,retestRuns:[good,good],requiredCleanRuns:2}).capabilityRequalification;
 assert.equal(r.action,'restore-capability');
});

test('too few clean retests keeps skill suspended',()=>{
 const r=capabilityRequalificationGate({beeId:'b1',capability:'archive-read',suspended:true,retestRuns:[good],requiredCleanRuns:2}).capabilityRequalification;
 assert.equal(r.action,'keep-capability-suspended');
});

test('recent failure resets recovery streak',()=>{
 const r=capabilityRequalificationGate({beeId:'b1',capability:'archive-read',suspended:true,retestRuns:[good,good,bad],requiredCleanRuns:2}).capabilityRequalification;
 assert.equal(r.cleanRecoveryStreak,0);
});

test('old failure does not block later clean recovery',()=>{
 const r=capabilityRequalificationGate({beeId:'b1',capability:'archive-read',suspended:true,retestRuns:[bad,good,good],requiredCleanRuns:2}).capabilityRequalification;
 assert.equal(r.action,'restore-capability');
});

test('bee retains unrelated capabilities during skill repair',()=>{
 const r=capabilityRequalificationGate({beeId:'b1',capability:'archive-read',suspended:true,retestRuns:[bad]}).capabilityRequalification;
 assert.equal(r.beeStatus,'retain-other-proven-capabilities');
});
