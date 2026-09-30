import test from 'node:test';
import assert from 'node:assert/strict';
import {backpressureGate} from '../core/backpressure_gate.mjs';

test('normal basket keeps feeding',()=>{
 const r=backpressureGate({basketId:'verify',queued:2,processingCapacity:2,highWaterMark:10}).backpressure;
 assert.equal(r.action,'feed');
});

test('high-water basket pauses only its own feed',()=>{
 const r=backpressureGate({basketId:'verify',queued:10,processingCapacity:2,highWaterMark:10}).backpressure;
 assert.equal(r.action,'pause-feed');
 assert.equal(r.scope,'local-basket-only');
});

test('paused basket remains held while backlog is high',()=>{
 const r=backpressureGate({basketId:'verify',queued:7,currentlyPaused:true,lowWaterMark:3}).backpressure;
 assert.equal(r.action,'hold-feed');
});

test('paused basket resumes after draining below low-water mark',()=>{
 const r=backpressureGate({basketId:'verify',queued:3,currentlyPaused:true,lowWaterMark:3}).backpressure;
 assert.equal(r.action,'resume-feed');
});

test('zero processing capacity is safely normalized',()=>{
 const r=backpressureGate({basketId:'verify',queued:5,processingCapacity:0}).backpressure;
 assert.equal(r.processingCapacity,1);
});
