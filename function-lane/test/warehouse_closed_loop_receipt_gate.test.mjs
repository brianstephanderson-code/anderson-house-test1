import test from 'node:test';
import assert from 'node:assert/strict';
import {warehouseClosedLoopReceiptGate} from '../core/warehouse_closed_loop_receipt_gate.mjs';

const good={jobId:'j1',doneState:'job-done-verified',marriageState:'loop-closed',copyState:'copy-loops-clean',originalRef:'orig-1',traceRef:'trace-1'};

test('fully closed job emits warehouse receipt',()=>{
 const r=warehouseClosedLoopReceiptGate(good).warehouseClosedLoopReceipt;
 assert.equal(r.state,'closed-loop-receipt-ready');
 assert.equal(r.receipt.status,'CLOSED');
});

test('unverified DONE blocks receipt',()=>{
 const r=warehouseClosedLoopReceiptGate({...good,doneState:'job-not-closed'}).warehouseClosedLoopReceipt;
 assert.equal(r.receipt,null);
});

test('unmarried trace blocks receipt',()=>{
 const r=warehouseClosedLoopReceiptGate({...good,marriageState:'marriage-gap'}).warehouseClosedLoopReceipt;
 assert.equal(r.state,'loop-still-open');
});

test('dangling communication copies block receipt',()=>{
 const r=warehouseClosedLoopReceiptGate({...good,copyState:'dangling-copies-remain'}).warehouseClosedLoopReceipt;
 assert.equal(r.action,'return-to-open-joint');
});

test('missing original or trace reference blocks receipt',()=>{
 const r=warehouseClosedLoopReceiptGate({...good,traceRef:null}).warehouseClosedLoopReceipt;
 assert.equal(r.receipt,null);
});
