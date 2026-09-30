import test from 'node:test';
import assert from 'node:assert/strict';
import { universeRecastGate } from '../core/universe_recast_gate.mjs';

test('sufficient evidence stops recast',()=>{
 assert.equal(universeRecastGate({sufficient:true}).universeRecast.action,'done');
});

test('productive search can first change query frame',()=>{
 const r=universeRecastGate({sufficient:false,queryFramesExhausted:false,usefulNewEvidenceLastCast:true}).universeRecast;
 assert.equal(r.action,'change-query-frame');
});

test('stalled frame can move to another meadow',()=>{
 const r=universeRecastGate({sufficient:false,queryFramesExhausted:true,currentMeadowExhausted:false,usefulNewEvidenceLastCast:false,alternateMeadows:['archive','end-user']}).universeRecast;
 assert.equal(r.action,'change-meadow');
 assert.deepEqual(r.targets,['archive','end-user']);
});

test('exhausted meadow can jump carrier universe',()=>{
 const r=universeRecastGate({sufficient:false,queryFramesExhausted:true,currentMeadowExhausted:true,alternateUniverses:['people','practice','place']}).universeRecast;
 assert.equal(r.action,'change-carrier-universe');
 assert.ok(r.targets.includes('practice'));
});

test('no known alternatives reopens carrier discovery',()=>{
 const r=universeRecastGate({sufficient:false,queryFramesExhausted:true,currentMeadowExhausted:true}).universeRecast;
 assert.equal(r.action,'open-carrier-cast');
});
