import test from 'node:test';
import assert from 'node:assert/strict';
import {beeDispatchGate} from '../core/bee_dispatch_gate.mjs';

test('independent small jobs are all ready in parallel',()=>{
 const r=beeDispatchGate({jobs:[
  {id:'time',function:'period fit'},
  {id:'place',function:'geography fit'},
  {id:'register',function:'register fit'}
 ]}).beeDispatch;
 assert.equal(r.parallelCapacity,3);
});

test('dependent bee waits for upstream done',()=>{
 const r=beeDispatchGate({jobs:[
  {id:'search',function:'cast',state:'working'},
  {id:'verify',function:'verify',dependsOn:['search']}
 ]}).beeDispatch;
 assert.deepEqual(r.waiting,['verify']);
});

test('dependency releases when upstream is done',()=>{
 const r=beeDispatchGate({jobs:[
  {id:'search',function:'cast',state:'done'},
  {id:'verify',function:'verify',dependsOn:['search']}
 ]}).beeDispatch;
 assert.deepEqual(r.ready,['verify']);
});

test('missing dependency repairs flow instead of guessing',()=>{
 const r=beeDispatchGate({jobs:[{id:'marry',function:'marry evidence',dependsOn:['unknown-job']}]}).beeDispatch;
 assert.equal(r.state,'repair-flow');
});

test('completed jobs are not redispatched',()=>{
 const r=beeDispatchGate({jobs:[{id:'done-one',function:'period fit',state:'done'}]}).beeDispatch;
 assert.equal(r.ready.length,0);
});
