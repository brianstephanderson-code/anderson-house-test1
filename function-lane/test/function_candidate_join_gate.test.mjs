import test from 'node:test';
import assert from 'node:assert/strict';
import {functionCandidateJoinGate} from '../core/function_candidate_join_gate.mjs';

test('candidates from many survey doors join into one fit-test basket',()=>{
 const r=functionCandidateJoinGate({returns:[
  {surveyDoor:'warehouse',candidates:[{functionId:'f1',provenance:'internal'}]},
  {surveyDoor:'bridge',candidates:[{functionId:'f2',provenance:'external'}]}
 ]}).functionCandidateJoin;
 assert.equal(r.state,'fit-test-ready');
 assert.equal(r.candidates.length,2);
});

test('same candidate from two doors is one candidate with two claims',()=>{
 const r=functionCandidateJoinGate({returns:[
  {surveyDoor:'warehouse',candidates:[{functionId:'f1',provenance:'internal'}]},
  {surveyDoor:'combo',candidates:[{functionId:'f1',provenance:'composition'}]}
 ]}).functionCandidateJoin;
 assert.equal(r.candidates.length,1);
 assert.equal(r.candidates[0].mentionCount,2);
});

test('multiple mentions do not preselect winner',()=>{
 const r=functionCandidateJoinGate({returns:[
  {surveyDoor:'a',candidates:[{functionId:'popular',provenance:'p1'}]},
  {surveyDoor:'b',candidates:[{functionId:'popular',provenance:'p2'}]},
  {surveyDoor:'c',candidates:[{functionId:'rare',provenance:'p3'}]}
 ]}).functionCandidateJoin;
 assert.equal('selectedFunction' in r,false);
});

test('candidate without provenance is rejected from fit basket',()=>{
 const r=functionCandidateJoinGate({returns:[{surveyDoor:'x',candidates:[{functionId:'f1'}]}]}).functionCandidateJoin;
 assert.equal(r.candidates.length,0);
 assert.equal(r.invalid.length,1);
});

test('empty returns trigger another O fanout cast',()=>{
 const r=functionCandidateJoinGate({returns:[]}).functionCandidateJoin;
 assert.equal(r.state,'recast-o-fanout');
});
