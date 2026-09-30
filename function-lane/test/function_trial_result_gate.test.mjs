import test from 'node:test';
import assert from 'node:assert/strict';
import {functionTrialResultGate} from '../core/function_trial_result_gate.mjs';

const pass={functionId:'f1',doneSatisfied:true,evidenceIntegrity:true,contextPreserved:true,errors:[],elapsed:12};

test('clean transformation qualifies',()=>{
 const r=functionTrialResultGate({results:[pass]}).functionTrialResult;
 assert.equal(r.qualified.length,1);
});

test('reaching done while damaging context fails',()=>{
 const r=functionTrialResultGate({results:[{...pass,functionId:'f2',contextPreserved:false}]}).functionTrialResult;
 assert.equal(r.failed.length,1);
});

test('evidence damage fails even when output looks right',()=>{
 const r=functionTrialResultGate({results:[{...pass,functionId:'f2',evidenceIntegrity:false}]}).functionTrialResult;
 assert.equal(r.failed.length,1);
});

test('incomplete measurement cannot qualify',()=>{
 const r=functionTrialResultGate({results:[{functionId:'f3',doneSatisfied:true}]}).functionTrialResult;
 assert.equal(r.incomplete.length,1);
});

test('multiple qualified functions are preserved without selecting one',()=>{
 const r=functionTrialResultGate({results:[pass,{...pass,functionId:'f2',elapsed:5}]}).functionTrialResult;
 assert.equal(r.qualified.length,2);
 assert.equal(r.selection,null);
});
