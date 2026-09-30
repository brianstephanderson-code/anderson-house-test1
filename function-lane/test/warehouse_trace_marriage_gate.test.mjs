import test from 'node:test';
import assert from 'node:assert/strict';
import {warehouseTraceMarriageGate} from '../core/warehouse_trace_marriage_gate.mjs';

const trace={jobId:'j1',checkpoints:['cp1'],evidence:['e1']};

test('one original plus proof closes the loop',()=>{
 const r=warehouseTraceMarriageGate({trace,originalJobs:[{jobId:'j1',originalRef:'orig-1'}]}).warehouseTraceMarriage;
 assert.equal(r.state,'loop-closed');
 assert.equal(r.originalRef,'orig-1');
});

test('missing original prevents archive',()=>{
 const r=warehouseTraceMarriageGate({trace,originalJobs:[]}).warehouseTraceMarriage;
 assert.equal(r.action,'hold-trace-and-reconcile-original');
});

test('duplicate originals expose an identity problem',()=>{
 const r=warehouseTraceMarriageGate({trace,originalJobs:[{jobId:'j1'},{jobId:'j1'}]}).warehouseTraceMarriage;
 assert.equal(r.originalMatches,2);
 assert.equal(r.state,'marriage-gap');
});

test('trace without checkpoint proof cannot close loop',()=>{
 const r=warehouseTraceMarriageGate({trace:{...trace,checkpoints:[]},originalJobs:[{jobId:'j1'}]}).warehouseTraceMarriage;
 assert.equal(r.proofReady,false);
});

test('trace without evidence cannot close loop',()=>{
 const r=warehouseTraceMarriageGate({trace:{...trace,evidence:[]},originalJobs:[{jobId:'j1'}]}).warehouseTraceMarriage;
 assert.equal(r.state,'marriage-gap');
});
