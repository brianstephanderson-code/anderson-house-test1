import test from 'node:test';
import assert from 'node:assert/strict';
import { contextIntegrityGate } from '../core/context_integrity_gate.mjs';

test('verified snippet with supporting surrounding context passes',()=>{
 const r=contextIntegrityGate({snippetVerified:true,surroundingContextChecked:true,contextSupportsClaim:true}).contextIntegrity;
 assert.equal(r.state,'context-intact');
});

test('snippet alone must be recast with context',()=>{
 const r=contextIntegrityGate({snippetVerified:true}).contextIntegrity;
 assert.equal(r.state,'recast-with-context');
});

test('lost negation is a context mismatch',()=>{
 const r=contextIntegrityGate({snippetVerified:true,surroundingContextChecked:true,negationLost:true}).contextIntegrity;
 assert.equal(r.state,'context-mismatch');
});

test('lost attribution is a context mismatch',()=>{
 const r=contextIntegrityGate({snippetVerified:true,surroundingContextChecked:true,speakerOrAttributionLost:true}).contextIntegrity;
 assert.equal(r.state,'context-mismatch');
});

test('irony risk without surrounding context forces high-risk recast',()=>{
 const r=contextIntegrityGate({snippetVerified:true,ironyOrQuotationRisk:true}).contextIntegrity;
 assert.equal(r.state,'high-risk-recast');
});
