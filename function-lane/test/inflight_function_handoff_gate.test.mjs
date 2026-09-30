import test from 'node:test';
import assert from 'node:assert/strict';
import {inflightFunctionHandoffGate} from '../core/inflight_function_handoff_gate.mjs';

const cp={id:'cp1',verified:true,functionContract:{done:'x'},inputs:{a:1},completedWork:{step1:'done'},evidence:['e1'],remainingWork:{step2:'todo'}};

test('verified checkpoint creates resumable handoff packet',()=>{
 const r=inflightFunctionHandoffGate({job:{id:'j1'},fromFunction:'a',toFunction:'b',checkpoint:cp}).inflightFunctionHandoff;
 assert.equal(r.state,'handoff-ready');
 assert.equal(r.action,'resume-with-replacement');
});

test('handoff preserves completed work',()=>{
 const r=inflightFunctionHandoffGate({job:{id:'j1'},checkpoint:cp}).inflightFunctionHandoff;
 assert.deepEqual(r.handoffPacket.completedWork,{step1:'done'});
});

test('handoff preserves evidence',()=>{
 const r=inflightFunctionHandoffGate({job:{id:'j1'},checkpoint:cp}).inflightFunctionHandoff;
 assert.deepEqual(r.handoffPacket.evidence,['e1']);
});

test('unverified checkpoint cannot be trusted for resume',()=>{
 const r=inflightFunctionHandoffGate({job:{id:'j1'},checkpoint:{...cp,verified:false}}).inflightFunctionHandoff;
 assert.equal(r.state,'checkpoint-required');
 assert.equal(r.handoffPacket,null);
});

test('missing remaining-work state blocks handoff',()=>{
 const {remainingWork,...broken}=cp;
 const r=inflightFunctionHandoffGate({job:{id:'j1'},checkpoint:broken}).inflightFunctionHandoff;
 assert.equal(r.action,'preserve-job-and-rebuild-checkpoint');
});
