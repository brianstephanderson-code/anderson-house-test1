import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipBridgeRequalificationGate} from '../core/relationship_bridge_requalification_gate.mjs';

const good={completed:true,contextKey:'speech-install',gapClosed:true,contextPreserved:true,evidenceSupported:true,extraAssumptions:false,errors:[]};
const bad={...good,gapClosed:false,errors:['miss']};

test('quarantined bridge returns after clean recovery streak',()=>{
 const r=relationshipBridgeRequalificationGate({bridgeId:'b1',contextKey:'speech-install',quarantined:true,retests:[good,good,good],requiredCleanRuns:3}).relationshipBridgeRequalification;
 assert.equal(r.action,'restore-bridge-context-pair');
});

test('too few clean retests keeps bridge quarantined',()=>{
 const r=relationshipBridgeRequalificationGate({bridgeId:'b1',contextKey:'speech-install',quarantined:true,retests:[good,good],requiredCleanRuns:3}).relationshipBridgeRequalification;
 assert.equal(r.action,'keep-bridge-context-quarantined');
});

test('recent miss resets bridge recovery streak',()=>{
 const r=relationshipBridgeRequalificationGate({bridgeId:'b1',contextKey:'speech-install',quarantined:true,retests:[good,good,bad],requiredCleanRuns:3}).relationshipBridgeRequalification;
 assert.equal(r.cleanRecoveryStreak,0);
});

test('old miss does not block later clean bridge recovery',()=>{
 const r=relationshipBridgeRequalificationGate({bridgeId:'b1',contextKey:'speech-install',quarantined:true,retests:[bad,good,good,good],requiredCleanRuns:3}).relationshipBridgeRequalification;
 assert.equal(r.action,'restore-bridge-context-pair');
});

test('retests from another context do not falsely restore this pair',()=>{
 const other={...good,contextKey:'other-context'};
 const r=relationshipBridgeRequalificationGate({bridgeId:'b1',contextKey:'speech-install',quarantined:true,retests:[other,other,other],requiredCleanRuns:3}).relationshipBridgeRequalification;
 assert.equal(r.completedRetests,0);
 assert.equal(r.action,'keep-bridge-context-quarantined');
});
