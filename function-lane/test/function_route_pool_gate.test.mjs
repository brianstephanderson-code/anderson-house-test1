import test from 'node:test';
import assert from 'node:assert/strict';
import {functionRoutePoolGate} from '../core/function_route_pool_gate.mjs';

const pool=[
 {functionId:'fast-web',supports:['speed','web'],available:true},
 {functionId:'archive-road',supports:['archive','deep-time'],available:true},
 {functionId:'local-corpus',supports:['offline','privacy'],available:true}
];

test('current state exposes compatible proven road',()=>{
 const r=functionRoutePoolGate({qualifiedFunctions:pool,stateNeeds:['archive','deep-time']}).functionRoutePool;
 assert.deepEqual(r.compatible,['archive-road']);
});

test('unavailable road is not offered',()=>{
 const r=functionRoutePoolGate({qualifiedFunctions:[{functionId:'x',supports:['speed'],available:false}],stateNeeds:['speed']}).functionRoutePool;
 assert.equal(r.compatible.length,0);
});

test('multiple compatible roads remain available',()=>{
 const r=functionRoutePoolGate({qualifiedFunctions:[
  {functionId:'a',supports:['search'],available:true},
  {functionId:'b',supports:['search'],available:true}
 ],stateNeeds:['search']}).functionRoutePool;
 assert.equal(r.compatible.length,2);
 assert.equal(r.permanentWinner,null);
});

test('no compatible road reopens O-gate instead of forcing bad fit',()=>{
 const r=functionRoutePoolGate({qualifiedFunctions:pool,stateNeeds:['unknown-capability']}).functionRoutePool;
 assert.equal(r.state,'open-o-gate');
});

test('empty needs preserves all currently available proven roads',()=>{
 const r=functionRoutePoolGate({qualifiedFunctions:pool,stateNeeds:[]}).functionRoutePool;
 assert.equal(r.compatible.length,3);
});
