import test from 'node:test';
import assert from 'node:assert/strict';
import { sourceStatusGate } from '../core/source_status_gate.mjs';

test('original direct record can establish primary status',()=>{
 const r=sourceStatusGate({sourceId:'record',directRelation:true,originalRecord:true,derivesFromEarlier:false}).sourceStatus;
 assert.equal(r.status,'primary-established');
});

test('oldest source found is not automatically primary',()=>{
 const r=sourceStatusGate({sourceId:'oldest-found',earlierSearchPerformed:true,earlierSourceFound:false}).sourceStatus;
 assert.equal(r.status,'earliest-known-not-primary-proven');
});

test('known dependence makes source derived',()=>{
 const r=sourceStatusGate({sourceId:'annotation-B',derivesFromEarlier:true}).sourceStatus;
 assert.equal(r.status,'secondary-or-derived');
});

test('finding an earlier source downgrades candidate origin',()=>{
 const r=sourceStatusGate({sourceId:'annotation-A',earlierSearchPerformed:true,earlierSourceFound:true}).sourceStatus;
 assert.equal(r.status,'secondary-or-derived');
});

test('unsupported primary label remains unresolved',()=>{
 const r=sourceStatusGate({sourceId:'page-X',claimedStatus:'primary'}).sourceStatus;
 assert.equal(r.status,'unresolved');
 assert.equal(r.primaryEstablished,false);
});
