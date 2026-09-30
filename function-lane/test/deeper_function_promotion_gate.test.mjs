import test from 'node:test';
import assert from 'node:assert/strict';
import {deeperFunctionPromotionGate} from '../core/deeper_function_promotion_gate.mjs';

const proven={state:'deeper-function-proven',candidateFunction:'nonwritten-knowledge-carrier',requirements:['preserve-nonwritten-transmission'],distinctClosedSignatures:3,cleanTrials:4};

test('proven deeper function becomes parent capability',()=>{
 const r=deeperFunctionPromotionGate({trialResult:proven,provenance:['trial-1']}).deeperFunctionPromotion;
 assert.equal(r.state,'parent-capability-ready');
 assert.equal(r.promoted.functionId,'nonwritten-knowledge-carrier');
});

test('proof boundary travels with promoted capability',()=>{
 const r=deeperFunctionPromotionGate({trialResult:proven}).deeperFunctionPromotion;
 assert.equal(r.promoted.scope,'only-within-proven-requirements-and-signature-family');
});

test('requirements remain attached to promoted function',()=>{
 const r=deeperFunctionPromotionGate({trialResult:proven}).deeperFunctionPromotion;
 assert.deepEqual(r.promoted.satisfies,['preserve-nonwritten-transmission']);
});

test('provenance survives promotion',()=>{
 const r=deeperFunctionPromotionGate({trialResult:proven,provenance:['g1','g2']}).deeperFunctionPromotion;
 assert.deepEqual(r.promoted.provenance,['g1','g2']);
});

test('unproven candidate cannot become parent capability',()=>{
 const r=deeperFunctionPromotionGate({trialResult:{...proven,state:'deeper-function-unproven'}}).deeperFunctionPromotion;
 assert.equal(r.promoted,null);
 assert.equal(r.state,'not-promotable');
});
