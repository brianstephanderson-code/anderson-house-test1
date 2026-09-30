import test from 'node:test';
import assert from 'node:assert/strict';
import {handoffContinuityVerificationGate} from '../core/handoff_continuity_verification_gate.mjs';

const packet={functionContract:{done:'x'},inputs:{a:1},completedWork:{s1:'done'},evidence:['e1'],remainingWork:{s2:'todo'}};
const resumed={functionContract:{done:'x'},inputs:{a:1},completedWork:{s1:'done'},evidence:['e1'],startingWork:{s2:'todo'}};

test('identical resumed state verifies continuity',()=>{
 const r=handoffContinuityVerificationGate({handoffPacket:packet,resumedState:resumed}).handoffContinuityVerification;
 assert.equal(r.state,'continuity-verified');
});

test('lost evidence blocks release',()=>{
 const r=handoffContinuityVerificationGate({handoffPacket:packet,resumedState:{...resumed,evidence:[]}}).handoffContinuityVerification;
 assert.equal(r.action,'stop-and-reconcile-handoff');
});

test('changed function contract is discontinuity',()=>{
 const r=handoffContinuityVerificationGate({handoffPacket:packet,resumedState:{...resumed,functionContract:{done:'y'}}}).handoffContinuityVerification;
 assert.equal(r.checks.sameContract,false);
});

test('replacement cannot silently redo completed work as starting work',()=>{
 const r=handoffContinuityVerificationGate({handoffPacket:packet,resumedState:{...resumed,startingWork:{s1:'done'}}}).handoffContinuityVerification;
 assert.equal(r.checks.startsAtRemaining,false);
});

test('changed inputs stop handoff continuity',()=>{
 const r=handoffContinuityVerificationGate({handoffPacket:packet,resumedState:{...resumed,inputs:{a:2}}}).handoffContinuityVerification;
 assert.equal(r.state,'handoff-discontinuity');
});
