import test from 'node:test';
import assert from 'node:assert/strict';
import { warehouseRecheck } from '../core/warehouse_recheck.mjs';

const good={finding:'verified finding',origin:'our-research',evidencePassport:{state:'verified'},logicTrace:['claim','evidence','context','verify']};
const old={finding:'old untraceable answer',origin:'our-old-answer'};

test('warehouse leaves traceable DONE alone when nothing changed',()=>{
  const r=warehouseRecheck([good]).warehouseRecheck;
  assert.equal(r.currentDone.length,1);
  assert.equal(r.reopenBasket.length,0);
});

test('new testing function reopens traceable warehouse findings',()=>{
  const r=warehouseRecheck([good],{newTestFunction:true}).warehouseRecheck;
  assert.equal(r.reopenBasket.length,1);
});

test('untraceable legacy answer goes to recast basket',()=>{
  const r=warehouseRecheck([old]).warehouseRecheck;
  assert.equal(r.recastBasket.length,1);
});

test('mixed warehouse sorts findings into separate baskets',()=>{
  const r=warehouseRecheck([good,old]).warehouseRecheck;
  assert.equal(r.currentDone.length,1);
  assert.equal(r.recastBasket.length,1);
});
