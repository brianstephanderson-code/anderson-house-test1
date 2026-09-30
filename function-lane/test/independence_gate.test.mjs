import test from 'node:test';
import assert from 'node:assert/strict';
import { independenceGate } from '../core/independence_gate.mjs';

test('three echoes of one origin count as one road',()=>{
 const r=independenceGate([
  {id:'A',originId:'old-note-1'},
  {id:'B',originId:'old-note-1'},
  {id:'C',originId:'old-note-1'},
 ]).independence;
 assert.equal(r.sourceCount,3);
 assert.equal(r.independentRoads,1);
});

test('different origins count as independent roads',()=>{
 const r=independenceGate([
  {id:'Irving-usage',originId:'irving-primary'},
  {id:'period-dictionary',originId:'dictionary-primary'},
  {id:'historical-record',originId:'archive-primary'},
 ]).independence;
 assert.equal(r.independentRoads,3);
});

test('unknown ancestry is not silently counted independent',()=>{
 const r=independenceGate([{id:'glossary-A'}]).independence;
 assert.equal(r.independentRoads,0);
 assert.equal(r.state,'trace-origins');
});

test('mixed evidence separates known families and unresolved origins',()=>{
 const r=independenceGate([
  {id:'A',originId:'root-1'},
  {id:'B',originId:'root-1'},
  {id:'C',originId:'root-2'},
  {id:'D'},
 ]).independence;
 assert.equal(r.independentRoads,2);
 assert.deepEqual(r.unresolvedOrigins,['D']);
});
