import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipBridgeJoinGate} from '../core/relationship_bridge_join_gate.mjs';

test('bridges from different universes enter one test basket',()=>{
 const r=relationshipBridgeJoinGate({returns:[
  {universe:'phonetic',candidates:[{bridgeId:'b1',provenance:'sound-match'}]},
  {universe:'functional',candidates:[{bridgeId:'b2',provenance:'same-role'}]}
 ]}).relationshipBridgeJoin;
 assert.equal(r.candidates.length,2);
 assert.equal(r.state,'bridge-test-ready');
});

test('same bridge found in two universes merges but preserves both',()=>{
 const r=relationshipBridgeJoinGate({returns:[
  {universe:'semantic',candidates:[{bridgeId:'b1',provenance:'p1'}]},
  {universe:'cultural',candidates:[{bridgeId:'b1',provenance:'p2'}]}
 ]}).relationshipBridgeJoin;
 assert.equal(r.candidates.length,1);
 assert.equal(r.candidates[0].crossUniverse,true);
 assert.deepEqual(r.candidates[0].universes,['semantic','cultural']);
});

test('support and contradiction remain visible together',()=>{
 const r=relationshipBridgeJoinGate({returns:[
  {universe:'historical',candidates:[{bridgeId:'b1',provenance:'p1',stance:'supports'}]},
  {universe:'cultural',candidates:[{bridgeId:'b1',provenance:'p2',stance:'contradicts'}]}
 ]}).relationshipBridgeJoin;
 assert.equal(r.candidates[0].contested,true);
});

test('candidate without provenance cannot enter bridge test basket',()=>{
 const r=relationshipBridgeJoinGate({returns:[{universe:'phonetic',candidates:[{bridgeId:'b1'}]}]}).relationshipBridgeJoin;
 assert.equal(r.candidates.length,0);
 assert.equal(r.invalid.length,1);
});

test('join gate never chooses the bridge',()=>{
 const r=relationshipBridgeJoinGate({returns:[{universe:'phonetic',candidates:[{bridgeId:'b1',provenance:'p'}]}]}).relationshipBridgeJoin;
 assert.equal(r.selection,null);
});
