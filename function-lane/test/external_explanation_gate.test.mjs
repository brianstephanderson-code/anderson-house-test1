import test from 'node:test';
import assert from 'node:assert/strict';
import { testExternalExplanation } from '../core/external_explanation_gate.mjs';

test('outside glossary conclusion without visible logic is recast', () => {
  const x=testExternalExplanation({term:'apparition',proposedMeaning:'ghost',source:'edition-A'}).externalExplanation;
  assert.equal(x.state,'recast');
});

test('outside explanation with logic but unresolved context stays pending', () => {
  const x=testExternalExplanation({term:'apparition',proposedMeaning:'ghost',source:'edition-B',logicTrace:['historical dictionary','local sentence'],provenanceTraceable:true}).externalExplanation;
  assert.equal(x.state,'logic-pending');
});

test('context failure rejects even a traceable outside explanation', () => {
  const x=testExternalExplanation({term:'Tappan Zee',proposedMeaning:'a bridge',source:'reader-note',logicTrace:['modern usage'],contextFit:'no',provenanceTraceable:true}).externalExplanation;
  assert.equal(x.state,'rejected');
});

test('matching logic only becomes a supported candidate, never automatic truth', () => {
  const x=testExternalExplanation({term:'St. Nicholas',proposedMeaning:'protective figure invoked by sailors',source:'annotated-edition',logicTrace:['Irving context','historical patronage evidence'],contextFit:'yes',provenanceTraceable:true}).externalExplanation;
  assert.equal(x.state,'candidate-supported');
  assert.notEqual(x.state,'verified');
});
