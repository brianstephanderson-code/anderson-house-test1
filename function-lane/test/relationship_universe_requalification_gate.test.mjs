import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipUniverseRequalificationGate} from '../core/relationship_universe_requalification_gate.mjs';

const good=id=>({completed:true,scopeKey:'speech',gapId:id,validBridgeProduced:true,contextPreserved:true,provenancePreserved:true,extraAssumptions:false,errors:[]});
const bad=id=>({...good(id),validBridgeProduced:false,errors:['miss']});

test('quarantined universe returns after clean distinct-gap retests',()=>{
 const r=relationshipUniverseRequalificationGate({universe:'phonetic',scopeKey:'speech',quarantined:true,retests:[good('g1'),good('g2'),good('g3')]}).relationshipUniverseRequalification;
 assert.equal(r.action,'restore-universe-scope-pair');
});

test('repeating one easy gap cannot restore a universe',()=>{
 const r=relationshipUniverseRequalificationGate({universe:'phonetic',scopeKey:'speech',quarantined:true,retests:[good('g1'),good('g1'),good('g1')]}).relationshipUniverseRequalification;
 assert.equal(r.action,'keep-universe-scope-quarantined');
});

test('failed retest does not count toward clean gap coverage',()=>{
 const r=relationshipUniverseRequalificationGate({universe:'phonetic',scopeKey:'speech',quarantined:true,retests:[good('g1'),good('g2'),bad('g3')]}).relationshipUniverseRequalification;
 assert.equal(r.distinctCleanGaps,2);
});

test('another scope cannot requalify this universe/scope pair',()=>{
 const other={...good('g3'),scopeKey:'music'};
 const r=relationshipUniverseRequalificationGate({universe:'phonetic',scopeKey:'speech',quarantined:true,retests:[good('g1'),good('g2'),other]}).relationshipUniverseRequalification;
 assert.equal(r.action,'keep-universe-scope-quarantined');
});

test('healthy nonquarantined universe is not needlessly restored',()=>{
 const r=relationshipUniverseRequalificationGate({universe:'phonetic',scopeKey:'speech',quarantined:false,retests:[good('g1'),good('g2'),good('g3')]}).relationshipUniverseRequalification;
 assert.equal(r.action,'universe-not-quarantined');
});
