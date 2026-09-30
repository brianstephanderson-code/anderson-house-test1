import test from 'node:test';
import assert from 'node:assert/strict';
import { verificationGate } from '../core/verification_gate.mjs';

test('copies from one origin remain one evidence road', () => {
  const out = verificationGate({
    claim:'example claim',
    contextFit:true,
    contradictionCheck:true,
    sources:[
      {id:'a',origin:'original-X',supportsExactClaim:true,provenanceChecked:true},
      {id:'b',origin:'original-X',supportsExactClaim:true,provenanceChecked:true},
      {id:'c',origin:'original-X',supportsExactClaim:true,provenanceChecked:true},
    ],
  }).verification;
  assert.equal(out.independentOriginCount,1);
  assert.equal(out.state,'single-road');
});

test('independent verified roads can pass the gate', () => {
  const out = verificationGate({
    claim:'example claim', contextFit:true, contradictionCheck:true,
    sources:[
      {id:'primary',origin:'archive-A',kind:'primary',supportsExactClaim:true,provenanceChecked:true},
      {id:'independent',origin:'scholar-B',kind:'secondary',supportsExactClaim:true,provenanceChecked:true},
    ],
  }).verification;
  assert.equal(out.independentOriginCount,2);
  assert.equal(out.state,'verified');
});

test('contradiction check cannot be skipped', () => {
  const out = verificationGate({
    claim:'example claim', contextFit:true, contradictionCheck:'pending',
    sources:[{id:'a',origin:'A',supportsExactClaim:true,provenanceChecked:true}],
  }).verification;
  assert.equal(out.state,'uncertain');
});
