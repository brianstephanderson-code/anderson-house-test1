import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipUniversePoolGate} from '../core/relationship_universe_pool_gate.mjs';

const universes=[
 {name:'phonetic',proven:true,available:true,scopeRequires:['speech-input'],provenance:'trial-set-1'},
 {name:'gesture',proven:true,available:true,scopeRequires:['observed-human-action'],provenance:'trial-set-2'},
 {name:'functional',proven:true,available:true,scopeRequires:[],provenance:'trial-set-3'}
];

test('matching context exposes proven universe',()=>{
 const r=relationshipUniversePoolGate({universes,contextTags:['speech-input']}).relationshipUniversePool;
 assert.ok(r.compatible.includes('phonetic'));
});

test('proven universe outside scope is not routed',()=>{
 const r=relationshipUniversePoolGate({universes,contextTags:['written-text']}).relationshipUniversePool;
 assert.equal(r.compatible.includes('phonetic'),false);
});

test('scope-free proven universe remains reusable',()=>{
 const r=relationshipUniversePoolGate({universes,contextTags:['anything']}).relationshipUniversePool;
 assert.ok(r.compatible.includes('functional'));
});

test('unproven universe cannot enter reusable pool',()=>{
 const r=relationshipUniversePoolGate({universes:[{name:'ritual',proven:false,available:true}],contextTags:[]}).relationshipUniversePool;
 assert.equal(r.proven.length,0);
});

test('provenance travels with reusable universe',()=>{
 const r=relationshipUniversePoolGate({universes,contextTags:['observed-human-action']}).relationshipUniversePool;
 assert.equal(r.provenance.gesture,'trial-set-2');
});
