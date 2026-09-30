import test from 'node:test';
import assert from 'node:assert/strict';
import {childFunctionTrialGate} from '../core/child_function_trial_gate.mjs';

const good={completed:true,signature:'database',holeClosed:true,requirementsSatisfied:true,contextPreserved:true,provenancePreserved:true,extraAssumptions:false};
const bad={...good,holeClosed:false};

test('child qualifies after repeated clean closures on parent boundary',()=>{
 const r=childFunctionTrialGate({parentFunction:'carrier',candidateChild:'database-carrier',boundarySignature:'database',trials:[good,good,good]}).childFunctionTrial;
 assert.equal(r.state,'child-function-proven');
 assert.equal(r.action,'attach-child-to-parent');
});

test('too few clean runs does not promote child',()=>{
 const r=childFunctionTrialGate({parentFunction:'carrier',candidateChild:'database-carrier',boundarySignature:'database',trials:[good,good]}).childFunctionTrial;
 assert.equal(r.state,'child-function-unproven');
});

test('failure at boundary does not count as clean child proof',()=>{
 const r=childFunctionTrialGate({parentFunction:'carrier',candidateChild:'database-carrier',boundarySignature:'database',trials:[good,good,bad]}).childFunctionTrial;
 assert.equal(r.cleanRuns,2);
});

test('trials from another boundary do not falsely prove child',()=>{
 const other={...good,signature:'music'};
 const r=childFunctionTrialGate({parentFunction:'carrier',candidateChild:'database-carrier',boundarySignature:'database',trials:[good,good,other]}).childFunctionTrial;
 assert.equal(r.completedTrials,2);
});

test('healthy parent remains active during child qualification',()=>{
 const r=childFunctionTrialGate({parentFunction:'carrier',candidateChild:'database-carrier',boundarySignature:'database',trials:[good]}).childFunctionTrial;
 assert.equal(r.parentAction,'keep-healthy-parent-active');
});
