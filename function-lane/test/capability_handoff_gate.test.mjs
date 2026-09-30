import test from 'node:test';
import assert from 'node:assert/strict';
import {capabilityHandoffGate} from '../core/capability_handoff_gate.mjs';

const clean={fromBee:'b1',toBee:'b2',statePreserved:true,evidencePreserved:true,contextPreserved:true,nextCapabilityMatches:true};

test('clean handoff passes',()=>{
 const r=capabilityHandoffGate({handoffs:[clean]}).capabilityHandoff;
 assert.equal(r.state,'handoffs-clean');
 assert.equal(r.accepted.length,1);
});

test('lost evidence blocks handoff',()=>{
 const r=capabilityHandoffGate({handoffs:[{...clean,evidencePreserved:false}]}).capabilityHandoff;
 assert.equal(r.state,'handoff-repair-required');
});

test('lost context blocks handoff even when state survives',()=>{
 const r=capabilityHandoffGate({handoffs:[{...clean,contextPreserved:false}]}).capabilityHandoff;
 assert.equal(r.blocked.length,1);
});

test('wrong next capability blocks routing',()=>{
 const r=capabilityHandoffGate({handoffs:[{...clean,nextCapabilityMatches:false}]}).capabilityHandoff;
 assert.equal(r.blocked.length,1);
});

test('one bad joint prevents chain from being declared clean',()=>{
 const r=capabilityHandoffGate({handoffs:[clean,{...clean,fromBee:'b2',toBee:'b3',statePreserved:false}]}).capabilityHandoff;
 assert.equal(r.accepted.length,1);
 assert.equal(r.blocked.length,1);
 assert.equal(r.state,'handoff-repair-required');
});
