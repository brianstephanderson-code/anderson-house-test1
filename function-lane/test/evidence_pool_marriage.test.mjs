import test from 'node:test';
import assert from 'node:assert/strict';
import { addEvidence } from '../core/evidence_pool.mjs';
import { marryEvidence } from '../core/evidence_marriage.mjs';

test('one evidence original is stored once', () => {
  const e={origin:'source-A',claim:'Nicholas patronage evidence',excerpt:'x'};
  const first=addEvidence([],e);
  const second=addEvidence(first.pool,e);
  assert.equal(first.pool.length,1);
  assert.equal(second.pool.length,1);
  assert.equal(second.added,false);
});

test('same pooled evidence can match one parcel and fail another', () => {
  const {item}=addEvidence([],{origin:'source-A',claim:'Nicholas patronage evidence',excerpt:'x'});
  const a=marryEvidence({parcel:{term:'St. Nicholas'},evidence:item,claimSupport:'yes',contextFit:'yes'}).marriage;
  const b=marryEvidence({parcel:{term:'Tappan Zee'},evidence:item,claimSupport:'no',contextFit:'no'}).marriage;
  assert.equal(a.state,'matched');
  assert.equal(b.state,'rejected');
  assert.equal(a.evidenceId,b.evidenceId);
});

test('uncertain fit stays pending rather than bluffing', () => {
  const {item}=addEvidence([],{origin:'source-B',claim:'historical usage',excerpt:'y'});
  const m=marryEvidence({parcel:{term:'apparition'},evidence:item,claimSupport:'yes',contextFit:'pending'}).marriage;
  assert.equal(m.state,'pending');
});
