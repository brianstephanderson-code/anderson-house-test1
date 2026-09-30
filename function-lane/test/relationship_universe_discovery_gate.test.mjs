import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipUniverseDiscoveryGate} from '../core/relationship_universe_discovery_gate.mjs';

const gap={left:'A',right:'B'};

test('novel relationship universe becomes a trial candidate',()=>{
 const r=relationshipUniverseDiscoveryGate({gap,knownUniverses:['semantic'],observations:[{proposedUniverse:'gesture',clue:'same hand movement',relationRule:'shared gesture',provenance:'field-note'}]}).relationshipUniverseDiscovery;
 assert.equal(r.candidates[0].universe,'gesture');
 assert.equal(r.state,'universe-trials-required');
});

test('known universe is not rediscovered as novel',()=>{
 const r=relationshipUniverseDiscoveryGate({gap,knownUniverses:['phonetic'],observations:[{proposedUniverse:'phonetic',clue:'sound'}]}).relationshipUniverseDiscovery;
 assert.equal(r.candidates.length,0);
});

test('candidate universe remains unproven until tested',()=>{
 const r=relationshipUniverseDiscoveryGate({gap,observations:[{proposedUniverse:'spatial',clue:'co-location'}]}).relationshipUniverseDiscovery;
 assert.equal(r.candidates[0].status,'unproven-universe');
});

test('provenance is preserved with universe proposal',()=>{
 const r=relationshipUniverseDiscoveryGate({gap,observations:[{proposedUniverse:'ritual',provenance:'oral-history-17'}]}).relationshipUniverseDiscovery;
 assert.equal(r.candidates[0].provenance,'oral-history-17');
});

test('no new universe widens observation net rather than forcing old map',()=>{
 const r=relationshipUniverseDiscoveryGate({gap,knownUniverses:['semantic'],observations:[]}).relationshipUniverseDiscovery;
 assert.equal(r.state,'widen-observation-net');
});
