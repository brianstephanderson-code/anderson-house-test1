import test from 'node:test';
import assert from 'node:assert/strict';
import {handoffDuplicateWorkGate} from '../core/handoff_duplicate_work_gate.mjs';

test('accepted completed work is blocked from replacement plan',()=>{
 const r=handoffDuplicateWorkGate({completedWork:['a','b'],plannedWork:['b','c']}).handoffDuplicateWork;
 assert.deepEqual(r.duplicates,['b']);
 assert.equal(r.state,'duplicate-work-blocked');
});

test('new unfinished work passes through',()=>{
 const r=handoffDuplicateWorkGate({completedWork:['a'],plannedWork:['b','c']}).handoffDuplicateWork;
 assert.deepEqual(r.remaining,['b','c']);
 assert.equal(r.state,'plan-clean');
});

test('explicitly invalidated old work may be redone',()=>{
 const r=handoffDuplicateWorkGate({completedWork:['a'],plannedWork:['a'],invalidatedWork:['a']}).handoffDuplicateWork;
 assert.deepEqual(r.legitimateRedo,['a']);
 assert.equal(r.duplicates.length,0);
});

test('invalidating one step does not reopen every completed step',()=>{
 const r=handoffDuplicateWorkGate({completedWork:['a','b'],plannedWork:['a','b'],invalidatedWork:['b']}).handoffDuplicateWork;
 assert.deepEqual(r.duplicates,['a']);
 assert.deepEqual(r.legitimateRedo,['b']);
});

test('empty replacement plan stays clean',()=>{
 const r=handoffDuplicateWorkGate({completedWork:['a'],plannedWork:[]}).handoffDuplicateWork;
 assert.equal(r.state,'plan-clean');
});
