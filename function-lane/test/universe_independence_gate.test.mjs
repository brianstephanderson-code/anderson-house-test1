import test from 'node:test';
import assert from 'node:assert/strict';
import {universeIndependenceGate} from '../core/universe_independence_gate.mjs';

test('different universes with same root are one evidence family',()=>{
 const r=universeIndependenceGate([
  {id:'book',universe:'document',ancestryRoot:'source-A'},
  {id:'modern-practice',universe:'practice',ancestryRoot:'source-A'}
 ]).universeIndependence;
 assert.equal(r.independentRoots,1);
 assert.equal(r.crossUniverseEchoes.length,1);
});

test('different universes with different roots remain independent',()=>{
 const r=universeIndependenceGate([
  {id:'archive',universe:'document',ancestryRoot:'root-1'},
  {id:'elder-account',universe:'people',ancestryRoot:'root-2'}
 ]).universeIndependence;
 assert.equal(r.independentRoots,2);
 assert.equal(r.crossUniverseEchoes.length,0);
});

test('same universe can still contain independent roots',()=>{
 const r=universeIndependenceGate([
  {id:'book-A',universe:'document',ancestryRoot:'root-1'},
  {id:'book-B',universe:'document',ancestryRoot:'root-2'}
 ]).universeIndependence;
 assert.equal(r.independentRoots,2);
});

test('unknown ancestry is not silently counted independent',()=>{
 const r=universeIndependenceGate([{id:'interview',universe:'people'}]).universeIndependence;
 assert.equal(r.independentRoots,0);
 assert.equal(r.state,'trace-universe-ancestry');
});

test('three carriers copied from one modern reconstruction count once',()=>{
 const r=universeIndependenceGate([
  {id:'website',universe:'digital',ancestryRoot:'reconstruction-X'},
  {id:'demonstration',universe:'practice',ancestryRoot:'reconstruction-X'},
  {id:'interview',universe:'people',ancestryRoot:'reconstruction-X'}
 ]).universeIndependence;
 assert.equal(r.independentRoots,1);
 assert.equal(r.crossUniverseEchoes[0].universes.length,3);
});
