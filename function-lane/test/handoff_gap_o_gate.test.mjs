import test from 'node:test';
import assert from 'node:assert/strict';
import {handoffGapOGate} from '../core/handoff_gap_o_gate.mjs';

const fromFunction={id:'search'};
const toFunction={id:'archive-read'};
const clean={statePreserved:true,evidencePreserved:true,contextPreserved:true,nextCapabilityMatches:true};

test('clean joint needs no bridge function',()=>{
 const r=handoffGapOGate({fromFunction,toFunction,handoff:clean}).handoffGapO;
 assert.equal(r.state,'joint-fits');
});

test('lost context creates context-carrier requirement',()=>{
 const r=handoffGapOGate({fromFunction,toFunction,handoff:{...clean,contextPreserved:false}}).handoffGapO;
 assert.ok(r.hole.requires.includes('preserve-context'));
});

test('evidence loss creates evidence preservation requirement',()=>{
 const r=handoffGapOGate({fromFunction,toFunction,handoff:{...clean,evidencePreserved:false}}).handoffGapO;
 assert.ok(r.hole.requires.includes('preserve-evidence'));
});

test('contract mismatch creates translation requirement',()=>{
 const r=handoffGapOGate({fromFunction,toFunction,handoff:{...clean,nextCapabilityMatches:false}}).handoffGapO;
 assert.ok(r.hole.requires.includes('translate-next-capability-contract'));
});

test('multiple broken properties describe one compound joint hole',()=>{
 const r=handoffGapOGate({fromFunction,toFunction,handoff:{statePreserved:false,evidencePreserved:false,contextPreserved:false,nextCapabilityMatches:false}}).handoffGapO;
 assert.equal(r.hole.requires.length,4);
 assert.equal(r.state,'cast-for-handoff-function');
});
