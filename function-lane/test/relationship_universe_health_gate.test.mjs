import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipUniverseHealthGate} from '../core/relationship_universe_health_gate.mjs';

const good={completed:true,scopeKey:'speech',validBridgeProduced:true,contextPreserved:true,provenancePreserved:true,extraAssumptions:false};
const bad={...good,validBridgeProduced:false};

test('healthy universe/scope pair stays available',()=>{
 const r=relationshipUniverseHealthGate({universe:'phonetic',scopeKey:'speech',recentCasts:[good,good,good,good]}).relationshipUniverseHealth;
 assert.equal(r.state,'universe-healthy');
});

test('degraded universe/scope pair is quarantined',()=>{
 const r=relationshipUniverseHealthGate({universe:'phonetic',scopeKey:'speech',recentCasts:[good,bad,bad,bad]}).relationshipUniverseHealth;
 assert.equal(r.action,'quarantine-universe-scope-pair');
});

test('another scope does not contaminate this measurement',()=>{
 const other={...bad,scopeKey:'music'};
 const r=relationshipUniverseHealthGate({universe:'phonetic',scopeKey:'speech',recentCasts:[good,good,good,good,other]}).relationshipUniverseHealth;
 assert.equal(r.failureRate,0);
});

test('hidden assumptions count as failed universe cast',()=>{
 const sneaky={...good,extraAssumptions:true};
 const r=relationshipUniverseHealthGate({universe:'phonetic',scopeKey:'speech',recentCasts:[good,sneaky,sneaky,sneaky]}).relationshipUniverseHealth;
 assert.equal(r.state,'universe-degraded');
});

test('too little history does not pretend universe certainty',()=>{
 const r=relationshipUniverseHealthGate({universe:'phonetic',scopeKey:'speech',recentCasts:[good],minCasts:4}).relationshipUniverseHealth;
 assert.equal(r.state,'insufficient-history');
});
