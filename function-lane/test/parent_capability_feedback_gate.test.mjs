import test from 'node:test';
import assert from 'node:assert/strict';
import {parentCapabilityFeedbackGate} from '../core/parent_capability_feedback_gate.mjs';

const good=s=>({completed:true,signature:s,holeClosed:true,contextPreserved:true,provenancePreserved:true,extraAssumptions:false});
const bad=s=>({...good(s),holeClosed:false});

test('successful reuse strengthens capability evidence',()=>{
 const r=parentCapabilityFeedbackGate({functionId:'carrier',uses:[good('oral'),good('gesture')]}).parentCapabilityFeedback;
 assert.equal(r.state,'capability-evidence-strengthened');
 assert.equal(r.successes,2);
});

test('successful new signature is learned',()=>{
 const r=parentCapabilityFeedbackGate({functionId:'carrier',uses:[good('demonstration')]}).parentCapabilityFeedback;
 assert.deepEqual(r.learnedSignatures,['demonstration']);
});

test('failed reuse becomes boundary signal',()=>{
 const r=parentCapabilityFeedbackGate({functionId:'carrier',uses:[bad('database')]}).parentCapabilityFeedback;
 assert.deepEqual(r.boundarySignals,['database']);
 assert.equal(r.state,'boundary-review-required');
});

test('hidden assumption counts as failed reuse',()=>{
 const r=parentCapabilityFeedbackGate({functionId:'carrier',uses:[{...good('ritual'),extraAssumptions:true}]}).parentCapabilityFeedback;
 assert.equal(r.failures,1);
});

test('duplicate evidence signatures collapse cleanly',()=>{
 const r=parentCapabilityFeedbackGate({functionId:'carrier',uses:[good('oral'),good('oral')]}).parentCapabilityFeedback;
 assert.deepEqual(r.learnedSignatures,['oral']);
});
