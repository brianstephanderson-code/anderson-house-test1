import test from 'node:test';
import assert from 'node:assert/strict';
import {idempotentParcelGate} from '../core/idempotent_parcel_gate.mjs';

test('identical duplicate return counts once',()=>{
 const p={jobId:'time-1',resultKey:'fit-yes',result:{fit:true}};
 const r=idempotentParcelGate({parcels:[p,{...p,workerId:'rescue-bee'}]}).idempotentParcel;
 assert.equal(r.accepted.length,1);
 assert.equal(r.duplicates.length,1);
});

test('retry of same logical result does not create downstream duplicate',()=>{
 const r=idempotentParcelGate({parcels:[
  {jobId:'archive-2',resultKey:'not-found',state:'not-found'},
  {jobId:'archive-2',resultKey:'not-found',state:'not-found'}
 ]}).idempotentParcel;
 assert.equal(r.accepted.length,1);
});

test('different results for same job become conflict, not silent overwrite',()=>{
 const r=idempotentParcelGate({parcels:[
  {jobId:'place-1',resultKey:'A',result:'Albany'},
  {jobId:'place-1',resultKey:'B',result:'Denmark'}
 ]}).idempotentParcel;
 assert.equal(r.state,'route-result-conflict');
 assert.equal(r.conflicts.length,1);
});

test('different jobs with same result remain separate',()=>{
 const r=idempotentParcelGate({parcels:[
  {jobId:'time-1',resultKey:'yes',result:true},
  {jobId:'place-1',resultKey:'yes',result:true}
 ]}).idempotentParcel;
 assert.equal(r.accepted.length,2);
});

test('result content can supply identity when explicit resultKey absent',()=>{
 const r=idempotentParcelGate({parcels:[
  {jobId:'x',result:{value:7}},
  {jobId:'x',result:{value:7}}
 ]}).idempotentParcel;
 assert.equal(r.duplicates.length,1);
});
