import test from 'node:test';
import assert from 'node:assert/strict';
import {crossUniverseConvergenceGate} from '../core/cross_universe_convergence_gate.mjs';

test('independent universes matching same detail create convergence',()=>{
 const r=crossUniverseConvergenceGate({findings:[
  {detail:'method used at night',universe:'document',ancestryRoot:'archive-A',contextFit:true,unexpectedDetail:true},
  {detail:'method used at night',universe:'people',ancestryRoot:'oral-line-B',contextFit:true,unexpectedDetail:true}
 ]}).crossUniverseConvergence;
 assert.equal(r.state,'independent-convergence-found');
 assert.equal(r.convergences[0].independentRoots,2);
});

test('same ancestry across universes is not qualified convergence',()=>{
 const r=crossUniverseConvergenceGate({findings:[
  {detail:'X',universe:'document',ancestryRoot:'root-1',contextFit:true},
  {detail:'X',universe:'practice',ancestryRoot:'root-1',contextFit:true}
 ]}).crossUniverseConvergence;
 assert.equal(r.state,'no-qualified-convergence');
});

test('same universe with different roots is not cross-universe convergence',()=>{
 const r=crossUniverseConvergenceGate({findings:[
  {detail:'X',universe:'document',ancestryRoot:'root-1',contextFit:true},
  {detail:'X',universe:'document',ancestryRoot:'root-2',contextFit:true}
 ]}).crossUniverseConvergence;
 assert.equal(r.state,'no-qualified-convergence');
});

test('context mismatch blocks convergence',()=>{
 const r=crossUniverseConvergenceGate({findings:[
  {detail:'X',universe:'document',ancestryRoot:'root-1',contextFit:true},
  {detail:'X',universe:'environment',ancestryRoot:'root-2',contextFit:false}
 ]}).crossUniverseConvergence;
 assert.equal(r.state,'no-qualified-convergence');
});

test('unexpected matching detail is preserved for later weighting',()=>{
 const r=crossUniverseConvergenceGate({findings:[
  {detail:'rare-detail',universe:'object',ancestryRoot:'root-1',contextFit:true},
  {detail:'rare-detail',universe:'practice',ancestryRoot:'root-2',contextFit:true,unexpectedDetail:true}
 ]}).crossUniverseConvergence;
 assert.equal(r.convergences[0].unexpected,true);
});
