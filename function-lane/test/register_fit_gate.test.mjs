import test from 'node:test';
import assert from 'node:assert/strict';
import { registerFitGate } from '../core/register_fit_gate.mjs';

test('matching register passes',()=>{
 const r=registerFitGate({targetRegister:'folklore',evidenceRegister:'folklore'}).registerFit;
 assert.equal(r.state,'register-fit');
});

test('ordinary dictionary sense alone does not establish specialist use',()=>{
 const r=registerFitGate({targetRegister:'nautical',evidenceRegister:'general'}).registerFit;
 assert.equal(r.state,'recast-domain-evidence');
});

test('known register difference raises mismatch risk',()=>{
 const r=registerFitGate({targetRegister:'legal',evidenceRegister:'general',registerDifferenceKnown:true}).registerFit;
 assert.equal(r.state,'register-mismatch-risk');
});

test('same sense can be bridged across registers with evidence',()=>{
 const r=registerFitGate({targetRegister:'religious',evidenceRegister:'general',sameSenseAcrossRegistersDemonstrated:true}).registerFit;
 assert.equal(r.state,'sense-bridged-across-registers');
});

test('explicit domain verification passes',()=>{
 const r=registerFitGate({targetRegister:'military',evidenceRegister:'historical dictionary',domainUsageVerified:true}).registerFit;
 assert.equal(r.state,'register-fit');
});
