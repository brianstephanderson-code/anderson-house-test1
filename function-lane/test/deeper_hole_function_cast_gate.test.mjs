import test from 'node:test';
import assert from 'node:assert/strict';
import {deeperHoleFunctionCastGate} from '../core/deeper_hole_function_cast_gate.mjs';

const cluster={clusterKey:'nonwritten',unmetRequirements:['preserve-nonwritten-transmission'],signatures:['oral','gesture','demonstration'],examples:['g1','g2']};

test('candidate functions inherit deeper unmet requirement',()=>{
 const r=deeperHoleFunctionCastGate({cluster,candidateFunctions:['embodied-knowledge-carrier']}).deeperHoleFunctionCast;
 assert.deepEqual(r.casts[0].mustSatisfy,['preserve-nonwritten-transmission']);
});

test('function is tested against all clustered surface signatures',()=>{
 const r=deeperHoleFunctionCastGate({cluster,candidateFunctions:['f1']}).deeperHoleFunctionCast;
 assert.deepEqual(r.casts[0].testAgainstSignatures,['oral','gesture','demonstration']);
});

test('many candidate functions can be cast in parallel',()=>{
 const r=deeperHoleFunctionCastGate({cluster,candidateFunctions:['f1','f2','f3']}).deeperHoleFunctionCast;
 assert.equal(r.casts.length,3);
});

test('gate does not choose a function before trials',()=>{
 const r=deeperHoleFunctionCastGate({cluster,candidateFunctions:['f1']}).deeperHoleFunctionCast;
 assert.equal(r.selection,null);
});

test('no candidate function opens function discovery',()=>{
 const r=deeperHoleFunctionCastGate({cluster,candidateFunctions:[]}).deeperHoleFunctionCast;
 assert.equal(r.state,'open-function-discovery');
});
