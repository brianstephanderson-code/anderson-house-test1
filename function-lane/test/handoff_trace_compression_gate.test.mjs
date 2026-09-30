import test from 'node:test';
import assert from 'node:assert/strict';
import {handoffTraceCompressionGate} from '../core/handoff_trace_compression_gate.mjs';

const events=[
 {sequence:1,type:'checkpoint',id:'cp1',verified:true,owner:'a',evidence:['e1']},
 {sequence:2,type:'handoff',from:'a',to:'b',checkpointId:'cp1'},
 {sequence:3,type:'checkpoint',id:'cp2',verified:true,owner:'b',evidence:['e2']},
 {sequence:4,type:'handoff',from:'b',to:'c',checkpointId:'cp2'}
];

test('multi-worker history compresses to one auditable trace',()=>{
 const r=handoffTraceCompressionGate({jobId:'j1',events}).handoffTraceCompression;
 assert.equal(r.state,'compressed-trace-ready');
 assert.equal(r.trace.handoffs.length,2);
});

test('verified checkpoints survive compression',()=>{
 const r=handoffTraceCompressionGate({jobId:'j1',events}).handoffTraceCompression;
 assert.deepEqual(r.trace.checkpoints,['cp1','cp2']);
});

test('evidence survives compression without duplicates',()=>{
 const r=handoffTraceCompressionGate({jobId:'j1',events:[...events,{sequence:5,type:'checkpoint',id:'cp3',verified:true,owner:'c',evidence:['e1']}]}).handoffTraceCompression;
 assert.deepEqual(r.trace.evidence,['e1','e2']);
});

test('ownership chain remains visible',()=>{
 const r=handoffTraceCompressionGate({jobId:'j1',events}).handoffTraceCompression;
 assert.deepEqual(r.trace.owners,['a','b','c']);
});

test('handoff without checkpoint reference blocks archive',()=>{
 const broken=[...events,{sequence:5,type:'handoff',from:'c',to:'d'}];
 const r=handoffTraceCompressionGate({jobId:'j1',events:broken}).handoffTraceCompression;
 assert.equal(r.state,'trace-gap');
});
