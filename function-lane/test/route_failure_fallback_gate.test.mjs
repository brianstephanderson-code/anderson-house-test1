import test from 'node:test';
import assert from 'node:assert/strict';
import {routeFailureFallbackGate} from '../core/route_failure_fallback_gate.mjs';

const pool=[
 {functionId:'road-a',qualified:true,available:true,supports:['search']},
 {functionId:'road-b',qualified:true,available:true,supports:['search']},
 {functionId:'road-c',qualified:true,available:true,supports:['archive']}
];

test('healthy active route continues',()=>{
 const r=routeFailureFallbackGate({activeFunctionId:'road-a',routePool:pool,stateNeeds:['search']}).routeFailureFallback;
 assert.equal(r.action,'continue-active-route');
});

test('failed route exposes compatible proven alternative',()=>{
 const r=routeFailureFallbackGate({activeFunctionId:'road-a',routePool:pool,stateNeeds:['search'],failure:'timeout'}).routeFailureFallback;
 assert.equal(r.action,'reroute-to-proven-alternative');
 assert.deepEqual(r.alternatives,['road-b']);
});

test('failed route never selects itself as fallback',()=>{
 const r=routeFailureFallbackGate({activeFunctionId:'road-a',routePool:pool,stateNeeds:['search'],failure:'error'}).routeFailureFallback;
 assert.equal(r.alternatives.includes('road-a'),false);
});

test('incompatible alternative is not exposed',()=>{
 const r=routeFailureFallbackGate({activeFunctionId:'road-a',routePool:pool,stateNeeds:['search'],failure:'error'}).routeFailureFallback;
 assert.equal(r.alternatives.includes('road-c'),false);
});

test('no proven fitting fallback reopens O-gate',()=>{
 const r=routeFailureFallbackGate({activeFunctionId:'road-a',routePool:pool,stateNeeds:['unknown'],failure:'error'}).routeFailureFallback;
 assert.equal(r.action,'open-o-gate');
});
