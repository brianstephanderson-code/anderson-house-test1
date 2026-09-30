import test from 'node:test';
import assert from 'node:assert/strict';
import {capabilityCompositionGate} from '../core/capability_composition_gate.mjs';

const job={id:'j1',requires:['search','archive-read','verify']};

test('separate bees can compose complete capability coverage',()=>{
 const r=capabilityCompositionGate({job,bees:[
  {id:'b1',capabilities:['search']},{id:'b2',capabilities:['archive-read']},{id:'b3',capabilities:['verify']}
 ]}).capabilityComposition;
 assert.equal(r.state,'composable-team-found');
 assert.deepEqual(r.missing,[]);
});

test('missing capability reopens capability O-gate',()=>{
 const r=capabilityCompositionGate({job,bees:[{id:'b1',capabilities:['search']},{id:'b2',capabilities:['verify']}]}).capabilityComposition;
 assert.deepEqual(r.missing,['archive-read']);
 assert.equal(r.state,'open-capability-o-gate');
});

test('unavailable bee cannot satisfy coverage',()=>{
 const r=capabilityCompositionGate({job,bees:[{id:'b1',capabilities:['search'],available:false},{id:'b2',capabilities:['archive-read','verify']}]}).capabilityComposition;
 assert.ok(r.missing.includes('search'));
});

test('multi-skilled bee may cover several requirements',()=>{
 const r=capabilityCompositionGate({job,bees:[{id:'b1',capabilities:['search','archive-read','verify']}]}).capabilityComposition;
 assert.deepEqual(r.team,['b1']);
});

test('composition declares explicit handoff preservation contract',()=>{
 const r=capabilityCompositionGate({job,bees:[]}).capabilityComposition;
 assert.equal(r.handoffContract,'preserve-state-evidence-context-between-capabilities');
});
