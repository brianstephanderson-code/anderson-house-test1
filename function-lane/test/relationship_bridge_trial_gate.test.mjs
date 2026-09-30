import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipBridgeTrialGate} from '../core/relationship_bridge_trial_gate.mjs';

const gap={left:'price in store',right:'install'};
const context={previousIntent:'install handoff gate'};

test('every candidate receives same original gap',()=>{
 const r=relationshipBridgeTrialGate({gap,context,candidates:[{bridgeId:'phonetic'},{bridgeId:'semantic'}]}).relationshipBridgeTrial;
 assert.equal(r.parallelCapacity,2);
 assert.ok(r.trials.every(t=>t.gap===gap));
});

test('every candidate receives same original context',()=>{
 const r=relationshipBridgeTrialGate({gap,context,candidates:[{bridgeId:'b1'},{bridgeId:'b2'}]}).relationshipBridgeTrial;
 assert.ok(r.trials.every(t=>t.context===context));
});

test('trial requires evidence and context, not resemblance alone',()=>{
 const r=relationshipBridgeTrialGate({gap,context,candidates:[{bridgeId:'b1'}]}).relationshipBridgeTrial;
 assert.ok(r.trials[0].doneContract.includes('evidence-supported'));
 assert.ok(r.trials[0].doneContract.includes('context-preserved'));
});

test('trial forbids hidden extra assumptions',()=>{
 const r=relationshipBridgeTrialGate({gap,context,candidates:[{bridgeId:'b1'}]}).relationshipBridgeTrial;
 assert.ok(r.trials[0].doneContract.includes('no-extra-assumptions'));
});

test('trial gate never preselects a bridge',()=>{
 const r=relationshipBridgeTrialGate({gap,context,candidates:[{bridgeId:'b1'}]}).relationshipBridgeTrial;
 assert.equal(r.selection,null);
});
