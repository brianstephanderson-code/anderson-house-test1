import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipBridgePoolGate} from '../core/relationship_bridge_pool_gate.mjs';

const bridges=[
 {bridgeId:'phonetic-install',contextRequires:['speech-input','installation-topic'],available:true},
 {bridgeId:'historical-name',contextRequires:['historical-source'],available:true},
 {bridgeId:'general-structural',contextRequires:[],available:true}
];

test('bridge is reusable when current context satisfies its proof boundary',()=>{
 const r=relationshipBridgePoolGate({qualifiedBridges:bridges,currentContextTags:['speech-input','installation-topic']}).relationshipBridgePool;
 assert.ok(r.compatible.includes('phonetic-install'));
});

test('phonetic bridge is not treated as universal outside its context',()=>{
 const r=relationshipBridgePoolGate({qualifiedBridges:bridges,currentContextTags:['historical-source']}).relationshipBridgePool;
 assert.equal(r.compatible.includes('phonetic-install'),false);
});

test('context-free proven bridge remains available across contexts',()=>{
 const r=relationshipBridgePoolGate({qualifiedBridges:bridges,currentContextTags:['anything']}).relationshipBridgePool;
 assert.ok(r.compatible.includes('general-structural'));
});

test('unavailable bridge is excluded even if context fits',()=>{
 const r=relationshipBridgePoolGate({qualifiedBridges:[{bridgeId:'b1',contextRequires:['x'],available:false}],currentContextTags:['x']}).relationshipBridgePool;
 assert.equal(r.compatible.length,0);
});

test('no fitting proven bridge triggers relationship recast',()=>{
 const r=relationshipBridgePoolGate({qualifiedBridges:[{bridgeId:'b1',contextRequires:['x'],available:true}],currentContextTags:['y']}).relationshipBridgePool;
 assert.equal(r.state,'recast-relationship-universes');
 assert.equal(r.universalBridge,null);
});
