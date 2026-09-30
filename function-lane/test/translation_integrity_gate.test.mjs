import test from 'node:test';
import assert from 'node:assert/strict';
import { translationIntegrityGate } from '../core/translation_integrity_gate.mjs';

test('translation tied back to verified original can pass',()=>{
 const r=translationIntegrityGate({originalLanguageAvailable:true,originalTextRef:'orig:p4',translatorIdentified:true,originalSenseVerified:true}).translationIntegrity;
 assert.equal(r.state,'translation-bridged');
});

test('available original should be checked before relying on translation',()=>{
 const r=translationIntegrityGate({originalLanguageAvailable:true}).translationIntegrity;
 assert.equal(r.state,'recast-original-language');
});

test('interpretive choice affecting claim raises contamination risk',()=>{
 const r=translationIntegrityGate({originalLanguageAvailable:true,originalTextRef:'orig:p4',translatorIdentified:true,interpretiveChoiceAffectsClaim:true,originalSenseVerified:false}).translationIntegrity;
 assert.equal(r.state,'translation-contamination-risk');
});

test('translation-only evidence is explicitly limited',()=>{
 const r=translationIntegrityGate({originalLanguageAvailable:false}).translationIntegrity;
 assert.equal(r.state,'translation-only-limited');
});

test('alternative translation check is preserved in passport',()=>{
 const r=translationIntegrityGate({originalLanguageAvailable:true,originalTextRef:'orig:p4',translatorIdentified:true,originalSenseVerified:true,alternativeTranslationsChecked:true}).translationIntegrity;
 assert.equal(r.alternativeTranslationsChecked,true);
});
