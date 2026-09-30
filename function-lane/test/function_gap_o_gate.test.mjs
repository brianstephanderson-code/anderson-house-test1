import test from 'node:test';
import assert from 'node:assert/strict';
import {functionGapOGate} from '../core/function_gap_o_gate.mjs';

const state={provides:['raw-term','sentence-context']};
const requiredDone={requires:['context-fit-definition']};

test('verified function fitting state and done is found',()=>{
 const r=functionGapOGate({state,requiredDone,candidates:[
  {id:'context-definition-fit',accepts:['raw-term','sentence-context'],produces:['context-fit-definition'],legal:true,verified:true}
 ]}).functionGapO;
 assert.equal(r.state,'function-fit-found');
});

test('familiar function that cannot make required done is rejected',()=>{
 const r=functionGapOGate({state,requiredDone,candidates:[
  {id:'dictionary-lookup',accepts:['raw-term'],produces:['generic-definition'],verified:true}
 ]}).functionGapO;
 assert.equal(r.state,'cast-more-functions');
});

test('function requiring unavailable state cannot fit',()=>{
 const r=functionGapOGate({state,requiredDone,candidates:[
  {id:'specialist-fit',accepts:['raw-term','missing-corpus'],produces:['context-fit-definition'],verified:true}
 ]}).functionGapO;
 assert.equal(r.fits.length,0);
});

test('unverified candidate cannot be installed merely because shape looks right',()=>{
 const r=functionGapOGate({state,requiredDone,candidates:[
  {id:'new-function',accepts:['raw-term'],produces:['context-fit-definition']}
 ]}).functionGapO;
 assert.equal(r.fits.length,0);
});

test('unsafe or disallowed candidate cannot fit',()=>{
 const r=functionGapOGate({state,requiredDone,candidates:[
  {id:'bad-route',accepts:['raw-term'],produces:['context-fit-definition'],verified:true,legal:false}
 ]}).functionGapO;
 assert.equal(r.state,'cast-more-functions');
});
