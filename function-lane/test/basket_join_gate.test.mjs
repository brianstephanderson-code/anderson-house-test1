import test from 'node:test';
import assert from 'node:assert/strict';
import {basketJoinGate} from '../core/basket_join_gate.mjs';

test('join opens when its required parcels have arrived',()=>{
 const r=basketJoinGate({requiredJobIds:['time','place'],parcels:[
  {jobId:'time',state:'done'},{jobId:'place',state:'done'}
 ]}).basketJoin;
 assert.equal(r.state,'join-ready');
});

test('join waits only for its missing dependency',()=>{
 const r=basketJoinGate({requiredJobIds:['time','place'],parcels:[{jobId:'time',state:'done'}]}).basketJoin;
 assert.deepEqual(r.missing,['place']);
});

test('unrelated unfinished work does not block join',()=>{
 const r=basketJoinGate({requiredJobIds:['time'],parcels:[
  {jobId:'time',state:'done'},
  {jobId:'translation',state:'working'}
 ]}).basketJoin;
 assert.equal(r.state,'join-ready');
 assert.equal(r.unrelatedParcelCount,1);
});

test('conflict parcel routes blocker instead of pretending join is clean',()=>{
 const r=basketJoinGate({requiredJobIds:['time','place'],parcels:[
  {jobId:'time',state:'done'},{jobId:'place',state:'conflict'}
 ]}).basketJoin;
 assert.equal(r.state,'route-blockers');
 assert.deepEqual(r.blockers,['place']);
});

test('not-found is a valid completed return and does not hang the hive',()=>{
 const r=basketJoinGate({requiredJobIds:['archive'],parcels:[{jobId:'archive',state:'not-found'}]}).basketJoin;
 assert.equal(r.state,'join-ready');
});
