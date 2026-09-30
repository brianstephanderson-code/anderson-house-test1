import test from 'node:test';
import assert from 'node:assert/strict';
import {crossUniverseMarriageGate} from '../core/cross_universe_marriage_gate.mjs';

test('two fitting carrier universes can become marriage candidate',()=>{
 const r=crossUniverseMarriageGate({findings:[
  {universe:'document',sameTarget:true,contextFit:true},
  {universe:'practice',sameTarget:true,contextFit:true}
 ]}).crossUniverseMarriage;
 assert.equal(r.state,'marriage-candidate');
});

test('two sources from same universe are not cross-universe marriage',()=>{
 const r=crossUniverseMarriageGate({findings:[
  {universe:'document',sameTarget:true,contextFit:true},
  {universe:'document',sameTarget:true,contextFit:true}
 ]}).crossUniverseMarriage;
 assert.equal(r.state,'needs-more-universes');
});

test('different universes do not marry if context differs',()=>{
 const r=crossUniverseMarriageGate({findings:[
  {universe:'people',sameTarget:true,contextFit:true},
  {universe:'environment',sameTarget:true,contextFit:false}
 ]}).crossUniverseMarriage;
 assert.equal(r.state,'needs-more-universes');
});

test('contradiction is preserved rather than averaged away',()=>{
 const r=crossUniverseMarriageGate({findings:[
  {universe:'document',sameTarget:true,contextFit:true},
  {universe:'people',sameTarget:true,contextFit:true,conflicts:true}
 ]}).crossUniverseMarriage;
 assert.equal(r.state,'hold-contradiction');
});

test('missing universe labels cannot manufacture independence',()=>{
 const r=crossUniverseMarriageGate({findings:[
  {sameTarget:true,contextFit:true},
  {sameTarget:true,contextFit:true}
 ]}).crossUniverseMarriage;
 assert.equal(r.state,'needs-more-universes');
});
