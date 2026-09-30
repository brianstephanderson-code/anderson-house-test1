import test from 'node:test';
import assert from 'node:assert/strict';
import {capabilityBoundarySplitGate} from '../core/capability_boundary_split_gate.mjs';

test('repeated same boundary creates child-function candidate',()=>{
 const r=capabilityBoundarySplitGate({functionId:'carrier',boundarySignals:[{id:'1',signature:'database'},{id:'2',signature:'database'}]}).capabilityBoundarySplit;
 assert.equal(r.childCandidates.length,1);
 assert.equal(r.state,'child-function-candidates-found');
});

test('single boundary miss does not overreact',()=>{
 const r=capabilityBoundarySplitGate({functionId:'carrier',boundarySignals:[{signature:'database'}]}).capabilityBoundarySplit;
 assert.equal(r.childCandidates.length,0);
});

test('different failure edges remain separate',()=>{
 const r=capabilityBoundarySplitGate({functionId:'carrier',boundarySignals:[{signature:'x'},{signature:'x'},{signature:'y'},{signature:'y'}]}).capabilityBoundarySplit;
 assert.equal(r.childCandidates.length,2);
});

test('requirements from repeated edge are collected for child discovery',()=>{
 const r=capabilityBoundarySplitGate({functionId:'carrier',boundarySignals:[{signature:'x',requirements:['a']},{signature:'x',requirements:['b']}]}).capabilityBoundarySplit;
 assert.deepEqual(r.childCandidates[0].requirements,['a','b']);
});

test('healthy parent stays active while child is discovered',()=>{
 const r=capabilityBoundarySplitGate({functionId:'carrier',boundarySignals:[{signature:'x'},{signature:'x'}]}).capabilityBoundarySplit;
 assert.equal(r.parentAction,'keep-healthy-parent-active');
});
