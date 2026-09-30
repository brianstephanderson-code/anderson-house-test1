import test from 'node:test';
import assert from 'node:assert/strict';
import {atomicFunctionGate} from '../core/atomic_function_gate.mjs';

test('splittable useful job is shredded further when cheap and safe',()=>{
 const r=atomicFunctionGate({job:'research time',independentlyTestable:true,usefulOutput:true,canSplitFurther:true,splitPreservesContext:true,splitReducesTotalCost:true}).atomicFunction;
 assert.equal(r.state,'shred-further');
});

test('small independently testable useful job is atomic ready',()=>{
 const r=atomicFunctionGate({job:'check period fit',independentlyTestable:true,usefulOutput:true,canSplitFurther:false}).atomicFunction;
 assert.equal(r.state,'atomic-ready');
});

test('do not split when context would be destroyed',()=>{
 const r=atomicFunctionGate({job:'interpret sentence in paragraph',independentlyTestable:true,usefulOutput:true,canSplitFurther:true,splitPreservesContext:false}).atomicFunction;
 assert.equal(r.state,'atomic-ready');
});

test('do not split when handoff cost dominates',()=>{
 const r=atomicFunctionGate({job:'tiny extraction',independentlyTestable:true,usefulOutput:true,canSplitFurther:true,splitPreservesContext:true,splitReducesTotalCost:true,handoffCostHigh:true}).atomicFunction;
 assert.equal(r.state,'atomic-ready');
});

test('job without useful independently testable output is recast',()=>{
 const r=atomicFunctionGate({job:'think about stuff',independentlyTestable:false,usefulOutput:false}).atomicFunction;
 assert.equal(r.state,'recast-job');
});
