import test from 'node:test';
import assert from 'node:assert/strict';
import {capabilityTrialGate} from '../core/capability_trial_gate.mjs';

const good={completed:true,doneSatisfied:true,evidenceIntegrity:true,contextPreserved:true,errors:[]};
const bad={completed:true,doneSatisfied:false,evidenceIntegrity:true,contextPreserved:true,errors:['fail']};

test('clean controlled trials prove capability',()=>{
 const r=capabilityTrialGate({beeId:'b1',capability:'archive-read',trials:[good,good],requiredCleanRuns:2}).capabilityTrial;
 assert.equal(r.state,'capability-proven');
 assert.equal(r.action,'add-to-capability-profile');
});

test('one claimed success is insufficient when two proofs required',()=>{
 const r=capabilityTrialGate({beeId:'b1',capability:'archive-read',trials:[good],requiredCleanRuns:2}).capabilityTrial;
 assert.equal(r.state,'capability-unproven');
});

test('failed controlled trial blocks live routing',()=>{
 const r=capabilityTrialGate({beeId:'b1',capability:'archive-read',trials:[good,bad],requiredCleanRuns:2}).capabilityTrial;
 assert.equal(r.action,'do-not-route-live-work');
});

test('context damage means capability is not proven',()=>{
 const r=capabilityTrialGate({beeId:'b1',capability:'archive-read',trials:[good,{...good,contextPreserved:false}],requiredCleanRuns:2}).capabilityTrial;
 assert.equal(r.state,'capability-unproven');
});

test('unfinished trial does not count as proof',()=>{
 const r=capabilityTrialGate({beeId:'b1',capability:'archive-read',trials:[good,{completed:false,doneSatisfied:true}],requiredCleanRuns:2}).capabilityTrial;
 assert.equal(r.completedTrials,1);
 assert.equal(r.state,'capability-unproven');
});
