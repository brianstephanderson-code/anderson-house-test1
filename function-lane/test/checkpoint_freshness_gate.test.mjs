import test from 'node:test';
import assert from 'node:assert/strict';
import {checkpointFreshnessGate} from '../core/checkpoint_freshness_gate.mjs';

const cp={id:'cp1',verified:true,inputVersion:'i1',contractVersion:'c1',ruleVersion:'r1',evidenceVersion:'e1'};
const current={inputVersion:'i1',contractVersion:'c1',ruleVersion:'r1',evidenceVersion:'e1'};

test('unchanged verified checkpoint may resume',()=>{
 const r=checkpointFreshnessGate({checkpoint:cp,current}).checkpointFreshness;
 assert.equal(r.state,'checkpoint-current');
 assert.equal(r.action,'allow-resume');
});

test('changed input makes checkpoint stale',()=>{
 const r=checkpointFreshnessGate({checkpoint:cp,current:{...current,inputVersion:'i2'}}).checkpointFreshness;
 assert.ok(r.stale.includes('inputVersion'));
});

test('changed function contract requires revalidation',()=>{
 const r=checkpointFreshnessGate({checkpoint:cp,current:{...current,contractVersion:'c2'}}).checkpointFreshness;
 assert.equal(r.action,'revalidate-from-last-safe-joint');
});

test('changed rule version blocks blind resume',()=>{
 const r=checkpointFreshnessGate({checkpoint:cp,current:{...current,ruleVersion:'r2'}}).checkpointFreshness;
 assert.ok(r.stale.includes('ruleVersion'));
});

test('unverified checkpoint is stale even if versions match',()=>{
 const r=checkpointFreshnessGate({checkpoint:{...cp,verified:false},current}).checkpointFreshness;
 assert.ok(r.stale.includes('verified'));
});
