import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipBridgeHealthGate} from '../core/relationship_bridge_health_gate.mjs';

const good={completed:true,contextKey:'speech-install',gapClosed:true,contextPreserved:true,evidenceSupported:true,extraAssumptions:false};
const bad={...good,gapClosed:false};

test('healthy bridge/context pair remains active',()=>{
 const r=relationshipBridgeHealthGate({bridgeId:'b1',contextKey:'speech-install',recentUses:[good,good,good]}).relationshipBridgeHealth;
 assert.equal(r.state,'bridge-healthy');
});

test('degraded bridge/context pair is quarantined',()=>{
 const r=relationshipBridgeHealthGate({bridgeId:'b1',contextKey:'speech-install',recentUses:[good,bad,bad]}).relationshipBridgeHealth;
 assert.equal(r.action,'quarantine-bridge-context-pair');
});

test('other contexts do not contaminate this bridge measurement',()=>{
 const other={...bad,contextKey:'different-context'};
 const r=relationshipBridgeHealthGate({bridgeId:'b1',contextKey:'speech-install',recentUses:[good,good,good,other]}).relationshipBridgeHealth;
 assert.equal(r.failureRate,0);
});

test('extra hidden assumptions count as bridge failure',()=>{
 const sneaky={...good,extraAssumptions:true};
 const r=relationshipBridgeHealthGate({bridgeId:'b1',contextKey:'speech-install',recentUses:[good,sneaky,sneaky]}).relationshipBridgeHealth;
 assert.equal(r.state,'bridge-degraded');
});

test('too little history does not pretend certainty',()=>{
 const r=relationshipBridgeHealthGate({bridgeId:'b1',contextKey:'speech-install',recentUses:[good],minUses:3}).relationshipBridgeHealth;
 assert.equal(r.state,'insufficient-history');
});
