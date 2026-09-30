import test from 'node:test';
import assert from 'node:assert/strict';
import {functionTrialFanoutGate} from '../core/function_trial_fanout_gate.mjs';

const stateParcel={term:'Saint Nicholas',context:'source sentence'};
const doneContract={requires:['context-fit-definition']};

test('all candidate functions receive same state and done contract',()=>{
 const r=functionTrialFanoutGate({stateParcel,doneContract,candidates:[{functionId:'f1'},{functionId:'f2'}]}).functionTrialFanout;
 assert.equal(r.parallelCapacity,2);
 assert.ok(r.trials.every(t=>t.stateParcel===stateParcel));
 assert.ok(r.trials.every(t=>t.doneContract===doneContract));
});

test('trial fanout does not preselect a winner',()=>{
 const r=functionTrialFanoutGate({stateParcel,doneContract,candidates:[{functionId:'f1'}]}).functionTrialFanout;
 assert.equal(r.selection,null);
});

test('candidate explicitly unsafe for trial is excluded',()=>{
 const r=functionTrialFanoutGate({stateParcel,doneContract,candidates:[{functionId:'safe'},{functionId:'blocked',verifiedForTrial:false}]}).functionTrialFanout;
 assert.deepEqual(r.trials.map(t=>t.functionId),['safe']);
});

test('missing state parcel blocks trials',()=>{
 const r=functionTrialFanoutGate({stateParcel:null,doneContract,candidates:[{functionId:'f1'}]}).functionTrialFanout;
 assert.equal(r.state,'repair-trial-inputs');
});

test('every trial carries identical measurement contract',()=>{
 const r=functionTrialFanoutGate({stateParcel,doneContract,candidates:[{functionId:'f1'},{functionId:'f2'}]}).functionTrialFanout;
 assert.deepEqual(r.trials[0].measurementContract,r.trials[1].measurementContract);
});
