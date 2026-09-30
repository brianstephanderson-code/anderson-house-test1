import test from 'node:test';
import assert from 'node:assert/strict';
import {handoffCompletionOwnershipGate} from '../core/handoff_completion_ownership_gate.mjs';

test('one active owner per unfinished unit closes ownership',()=>{
 const r=handoffCompletionOwnershipGate({remainingWork:['b','c'],assignments:[{functionId:'bee-b',active:true,work:['b','c']}]}).handoffCompletionOwnership;
 assert.equal(r.state,'ownership-closed');
});

test('unfinished unit with no owner is caught',()=>{
 const r=handoffCompletionOwnershipGate({remainingWork:['b','c'],assignments:[{functionId:'bee-b',active:true,work:['b']}]}).handoffCompletionOwnership;
 assert.deepEqual(r.orphaned,['c']);
});

test('two active owners on same unit are caught',()=>{
 const r=handoffCompletionOwnershipGate({remainingWork:['b'],assignments:[{functionId:'bee-b',active:true,work:['b']},{functionId:'bee-c',active:true,work:['b']}]}).handoffCompletionOwnership;
 assert.deepEqual(r.duplicated,['b']);
});

test('inactive old worker does not count as second owner',()=>{
 const r=handoffCompletionOwnershipGate({remainingWork:['b'],assignments:[{functionId:'bee-a',active:false,work:['b']},{functionId:'bee-b',active:true,work:['b']}]}).handoffCompletionOwnership;
 assert.equal(r.state,'ownership-closed');
});

test('mixed orphan and duplicate requires reconciliation',()=>{
 const r=handoffCompletionOwnershipGate({remainingWork:['b','c'],assignments:[{functionId:'x',active:true,work:['b']},{functionId:'y',active:true,work:['b']}]}).handoffCompletionOwnership;
 assert.deepEqual(r.duplicated,['b']);
 assert.deepEqual(r.orphaned,['c']);
 assert.equal(r.action,'reconcile-work-ownership');
});
