import test from 'node:test';
import assert from 'node:assert/strict';
import { batchByFunction } from '../core/function_batcher.mjs';

test('batcher groups casts but preserves individual parcels', () => {
  const glossaryParcels = [{term:'apparition'}, {term:'bewitched'}];
  const namedParcels = [{term:'St. Nicholas'}, {term:'Tappan Zee'}];
  const out = batchByFunction({glossaryParcels,namedParcels}).functionBatches;
  assert.equal(out.length, 2);
  assert.equal(out.reduce((n,b)=>n+b.count,0), 4);
  assert.ok(out.every((b)=>/VERIFY EACH RETURN/.test(b.rule)));
  assert.equal(out.find((b)=>b.functionClass==='namedReferenceFunction').parcels[0].term,'St. Nicholas');
});
