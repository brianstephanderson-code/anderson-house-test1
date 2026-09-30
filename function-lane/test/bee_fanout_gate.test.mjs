import test from 'node:test';
import assert from 'node:assert/strict';
import {beeFanoutGate} from '../core/bee_fanout_gate.mjs';

test('time function fans out across different carriers',()=>{
 const r=beeFanoutGate({functionName:'time',casts:[
  {id:'archive-bee',target:'archived documents'},
  {id:'oral-bee',target:'intergenerational transmission'},
  {id:'practice-bee',target:'surviving practice'},
  {id:'place-bee',target:'landscape memory'},
  {id:'environment-bee',target:'environmental traces'}
 ]}).beeFanout;
 assert.equal(r.workerCount,5);
 assert.equal(r.independentWorkerCount,5);
});

test('same function is preserved across fanout',()=>{
 const r=beeFanoutGate({functionName:'verification',casts:[{id:'a',target:'source'},{id:'b',target:'context'}]}).beeFanout;
 assert.equal(r.functionName,'verification');
});

test('duplicate targets are visible',()=>{
 const r=beeFanoutGate({functionName:'time',casts:[{id:'a',target:'archives'},{id:'b',target:'archives'}]}).beeFanout;
 assert.equal(r.duplicateTargets,1);
});

test('dependent cast is not counted as independent worker',()=>{
 const r=beeFanoutGate({functionName:'time',casts:[{id:'a',target:'archive'},{id:'b',target:'verify archive',dependsOn:['a']}]}).beeFanout;
 assert.equal(r.independentWorkerCount,1);
});

test('empty fanout recasts',()=>{
 assert.equal(beeFanoutGate({functionName:'time'}).beeFanout.state,'recast-fanout');
});
