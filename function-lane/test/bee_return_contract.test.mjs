import test from 'node:test';
import assert from 'node:assert/strict';
import {beeReturnContract} from '../core/bee_return_contract.mjs';

const good={jobId:'time-17',functionName:'period-fit',workerId:'bee-9',state:'done',result:{fit:true},evidenceRefs:['source-1'],confidence:'medium'};

test('complete done parcel is accepted',()=>{
 assert.equal(beeReturnContract(good).beeReturn.accepted,true);
});

test('worker identity is carried but does not alter parcel shape',()=>{
 const a=beeReturnContract(good).beeReturn.parcel;
 const b=beeReturnContract({...good,workerId:'bee-44'}).beeReturn.parcel;
 assert.deepEqual(Object.keys(a),Object.keys(b));
});

test('done without result is rejected',()=>{
 const r=beeReturnContract({...good,result:null}).beeReturn;
 assert.equal(r.accepted,false);
 assert.ok(r.missing.includes('result'));
});

test('not-found may return without fabricated result',()=>{
 const r=beeReturnContract({...good,state:'not-found',result:null,evidenceRefs:[]}).beeReturn;
 assert.equal(r.accepted,true);
});

test('conflict and caveats survive handoff',()=>{
 const r=beeReturnContract({...good,state:'conflict',result:{a:'X',b:'Y'},caveats:['sources disagree'],nextSuggestedFunction:'contradiction-check'}).beeReturn;
 assert.equal(r.accepted,true);
 assert.equal(r.parcel.nextSuggestedFunction,'contradiction-check');
 assert.equal(r.parcel.caveats.length,1);
});
