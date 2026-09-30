import test from 'node:test';
import assert from 'node:assert/strict';
import { uncertaintyLaunderingGate } from '../core/uncertainty_laundering_gate.mjs';

test('possible becoming asserted without new evidence is caught',()=>{
 const r=uncertaintyLaunderingGate([
  {id:'scholar',claimStrength:'possible'},
  {id:'glossary',claimStrength:'asserted'},
 ]).uncertaintyLaundering;
 assert.equal(r.state,'confidence-inflation');
});

test('unchanged caution is clean',()=>{
 const r=uncertaintyLaunderingGate([
  {id:'A',claimStrength:'possible'},
  {id:'B',claimStrength:'possible'},
 ]).uncertaintyLaundering;
 assert.equal(r.state,'clean');
});

test('stronger claim is allowed when explicit independent evidence is added',()=>{
 const r=uncertaintyLaunderingGate([
  {id:'A',claimStrength:'possible'},
  {id:'B',claimStrength:'probable',newIndependentEvidence:true},
 ]).uncertaintyLaundering;
 assert.equal(r.state,'clean');
});

test('multi-step laundering catches the inflation step',()=>{
 const r=uncertaintyLaunderingGate([
  {id:'A',claimStrength:'possible'},
  {id:'B',claimStrength:'possible'},
  {id:'C',claimStrength:'certain'},
 ]).uncertaintyLaundering;
 assert.equal(r.violations.length,1);
 assert.equal(r.violations[0].to,'C');
});

test('weakening a claim is not laundering',()=>{
 const r=uncertaintyLaunderingGate([
  {id:'A',claimStrength:'probable'},
  {id:'B',claimStrength:'possible'},
 ]).uncertaintyLaundering;
 assert.equal(r.state,'clean');
});
