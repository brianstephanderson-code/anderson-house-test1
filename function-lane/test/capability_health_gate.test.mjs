import test from 'node:test';
import assert from 'node:assert/strict';
import {capabilityHealthGate} from '../core/capability_health_gate.mjs';

const good={completed:true,capability:'archive-read',doneSatisfied:true,evidenceIntegrity:true,contextPreserved:true,errors:[]};
const bad={...good,doneSatisfied:false,errors:['fail']};

test('healthy capability remains available',()=>{
 const r=capabilityHealthGate({beeId:'b1',capability:'archive-read',recentRuns:[good,good,good]}).capabilityHealth;
 assert.equal(r.state,'capability-healthy');
});

test('degraded skill is suspended for retest',()=>{
 const r=capabilityHealthGate({beeId:'b1',capability:'archive-read',recentRuns:[good,bad,bad]}).capabilityHealth;
 assert.equal(r.action,'suspend-capability-and-retest');
});

test('other capabilities do not contaminate this skill measurement',()=>{
 const other={...bad,capability:'search'};
 const r=capabilityHealthGate({beeId:'b1',capability:'archive-read',recentRuns:[good,good,good,other]}).capabilityHealth;
 assert.equal(r.failureRate,0);
});

test('too little evidence does not pretend capability certainty',()=>{
 const r=capabilityHealthGate({beeId:'b1',capability:'archive-read',recentRuns:[good],minRuns:3}).capabilityHealth;
 assert.equal(r.state,'insufficient-history');
});

test('bee keeps unrelated proven capabilities when one skill degrades',()=>{
 const r=capabilityHealthGate({beeId:'b1',capability:'archive-read',recentRuns:[bad,bad,bad]}).capabilityHealth;
 assert.equal(r.beeStatus,'retain-other-proven-capabilities');
});
