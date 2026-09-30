import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipBridgeResultGate} from '../core/relationship_bridge_result_gate.mjs';

const pass={bridgeId:'b1',leftConnectsToRight:true,contextPreserved:true,evidenceSupported:true,noExtraAssumptions:true};

test('bridge that closes gap cleanly qualifies',()=>{
 const r=relationshipBridgeResultGate({results:[pass]}).relationshipBridgeResult;
 assert.equal(r.qualified.length,1);
});

test('plausible bridge that requires extra assumption fails',()=>{
 const r=relationshipBridgeResultGate({results:[{...pass,bridgeId:'b2',noExtraAssumptions:false}]}).relationshipBridgeResult;
 assert.equal(r.failed.length,1);
});

test('bridge that loses original context fails',()=>{
 const r=relationshipBridgeResultGate({results:[{...pass,contextPreserved:false}]}).relationshipBridgeResult;
 assert.equal(r.failed.length,1);
});

test('missing evidence measurement remains incomplete rather than passing',()=>{
 const {evidenceSupported,...partial}=pass;
 const r=relationshipBridgeResultGate({results:[partial]}).relationshipBridgeResult;
 assert.equal(r.incomplete.length,1);
});

test('several clean bridges may qualify without choosing one',()=>{
 const r=relationshipBridgeResultGate({results:[pass,{...pass,bridgeId:'b2'}]}).relationshipBridgeResult;
 assert.equal(r.qualified.length,2);
 assert.equal(r.selection,null);
});
