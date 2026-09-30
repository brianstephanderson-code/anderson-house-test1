import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipUniverseRecastGate} from '../core/relationship_universe_recast_gate.mjs';

const gap={left:'price in store',right:'install'};

test('failed semantic cast can move to phonetic universe',()=>{
 const r=relationshipUniverseRecastGate({gap,triedUniverses:['semantic'],candidateUniverses:['semantic','phonetic','functional']}).relationshipUniverseRecast;
 assert.deepEqual(r.recastQueue,['phonetic','functional']);
});

test('already tried universes are not repeated',()=>{
 const r=relationshipUniverseRecastGate({gap,triedUniverses:['semantic','phonetic'],candidateUniverses:['phonetic','orthographic']}).relationshipUniverseRecast;
 assert.deepEqual(r.recastQueue,['orthographic']);
});

test('the same gap survives the universe change',()=>{
 const r=relationshipUniverseRecastGate({gap,triedUniverses:['semantic'],candidateUniverses:['phonetic']}).relationshipUniverseRecast;
 assert.equal(r.gap,gap);
});

test('available new universe produces recast state',()=>{
 const r=relationshipUniverseRecastGate({gap,candidateUniverses:['cultural']}).relationshipUniverseRecast;
 assert.equal(r.state,'recast-in-new-universe');
});

test('exhausted known universes asks for new universe discovery',()=>{
 const r=relationshipUniverseRecastGate({gap,triedUniverses:['semantic'],candidateUniverses:['semantic']}).relationshipUniverseRecast;
 assert.equal(r.state,'open-new-universe-search');
});
