import test from 'node:test';
import assert from 'node:assert/strict';
import {handoffCompletionReconciliationGate} from '../core/handoff_completion_reconciliation_gate.mjs';

const done=['research','transform','verify'];

test('all promised units with evidence closes job',()=>{
 const r=handoffCompletionReconciliationGate({doneContract:done,completedUnits:done,evidenceByUnit:{research:['e1'],transform:['e2'],verify:['e3']}}).handoffCompletionReconciliation;
 assert.equal(r.state,'job-done-verified');
});

test('missing promised unit keeps job open',()=>{
 const r=handoffCompletionReconciliationGate({doneContract:done,completedUnits:['research','transform'],evidenceByUnit:{research:['e1'],transform:['e2']}}).handoffCompletionReconciliation;
 assert.deepEqual(r.missing,['verify']);
});

test('claimed completion without evidence is not closed',()=>{
 const r=handoffCompletionReconciliationGate({doneContract:done,completedUnits:done,evidenceByUnit:{research:['e1'],transform:[],verify:['e3']}}).handoffCompletionReconciliation;
 assert.deepEqual(r.withoutEvidence,['transform']);
});

test('extra work is visible but does not replace promised work',()=>{
 const r=handoffCompletionReconciliationGate({doneContract:done,completedUnits:['research','transform','extra'],evidenceByUnit:{research:['e1'],transform:['e2'],extra:['x']}}).handoffCompletionReconciliation;
 assert.deepEqual(r.extras,['extra']);
 assert.deepEqual(r.missing,['verify']);
});

test('recovery reopens only missing or unverified units',()=>{
 const r=handoffCompletionReconciliationGate({doneContract:done,completedUnits:['research','transform'],evidenceByUnit:{research:['e1'],transform:['e2']}}).handoffCompletionReconciliation;
 assert.equal(r.action,'reopen-only-missing-or-unverified-units');
});
