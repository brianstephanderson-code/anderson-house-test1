import test from 'node:test';
import assert from 'node:assert/strict';
import {deeperHoleFunctionTrialGate} from '../core/deeper_hole_function_trial_gate.mjs';

const good=s=>({completed:true,signature:s,holeClosed:true,requirementsSatisfied:true,contextPreserved:true,provenancePreserved:true,extraAssumptions:false});

test('function proven when it closes different surface holes',()=>{
 const r=deeperHoleFunctionTrialGate({candidateFunction:'carrier',trials:[good('oral'),good('gesture')]}).deeperHoleFunctionTrial;
 assert.equal(r.state,'deeper-function-proven');
});

test('repeating same surface hole does not prove deeper explanation',()=>{
 const r=deeperHoleFunctionTrialGate({candidateFunction:'carrier',trials:[good('oral'),good('oral')]}).deeperHoleFunctionTrial;
 assert.equal(r.state,'deeper-function-unproven');
});

test('hidden assumption prevents a clean closure',()=>{
 const r=deeperHoleFunctionTrialGate({candidateFunction:'carrier',trials:[good('oral'),{...good('gesture'),extraAssumptions:true}]}).deeperHoleFunctionTrial;
 assert.equal(r.distinctClosedSignatures,1);
});

test('loss of provenance prevents promotion',()=>{
 const r=deeperHoleFunctionTrialGate({candidateFunction:'carrier',trials:[good('oral'),{...good('gesture'),provenancePreserved:false}]}).deeperHoleFunctionTrial;
 assert.equal(r.action,'keep-testing-or-recast');
});

test('threshold can require broader cross-hole proof',()=>{
 const r=deeperHoleFunctionTrialGate({candidateFunction:'carrier',trials:[good('oral'),good('gesture')],requiredDistinctSignatures:3}).deeperHoleFunctionTrial;
 assert.equal(r.state,'deeper-function-unproven');
});
