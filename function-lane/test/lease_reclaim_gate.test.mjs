import test from 'node:test';
import assert from 'node:assert/strict';
import {leaseReclaimGate} from '../core/lease_reclaim_gate.mjs';

const now=10000;

test('expired working job returns to ready pool',()=>{
 const r=leaseReclaimGate({now,jobs:[{id:'j1',state:'working',workerId:'bee-1',leaseExpiresAt:9000}]}).leaseReclaim;
 assert.equal(r.state,'jobs-reclaimed');
 assert.equal(r.reclaimed[0].jobId,'j1');
});

test('healthy lease remains with current bee',()=>{
 const r=leaseReclaimGate({now,jobs:[{id:'j1',state:'working',workerId:'bee-1',leaseExpiresAt:11000}]}).leaseReclaim;
 assert.deepEqual(r.leased,['j1']);
});

test('completed job is never reclaimed',()=>{
 const r=leaseReclaimGate({now,jobs:[{id:'j1',state:'done',workerId:'bee-1',leaseExpiresAt:9000}]}).leaseReclaim;
 assert.equal(r.reclaimed.length,0);
 assert.deepEqual(r.completed,['j1']);
});

test('worker identity is preserved for audit when reclaiming',()=>{
 const r=leaseReclaimGate({now,jobs:[{id:'j1',state:'working',workerId:'cloud-bee-7',leaseExpiresAt:1}]}).leaseReclaim;
 assert.equal(r.reclaimed[0].formerWorkerId,'cloud-bee-7');
});

test('nonworking queued job is left for normal dispatch',()=>{
 const r=leaseReclaimGate({now,jobs:[{id:'j1',state:'ready'}]}).leaseReclaim;
 assert.equal(r.reclaimed.length,0);
});
