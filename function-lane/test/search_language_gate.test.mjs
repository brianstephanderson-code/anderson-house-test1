import test from 'node:test';
import assert from 'node:assert/strict';
import { searchLanguageGate } from '../core/search_language_gate.mjs';

test('missing relevant language forces recast',()=>{
 const r=searchLanguageGate({relevantLanguages:['English','Dutch'],searchedLanguages:['English']}).searchLanguage;
 assert.equal(r.state,'recast-query-language');
 assert.deepEqual(r.gaps.languages,['Dutch']);
});

test('historical spelling gap is detected',()=>{
 const r=searchLanguageGate({historicalFormsExpected:['St. Nicholas','Sint Nicolaas'],searchedHistoricalForms:['St. Nicholas']}).searchLanguage;
 assert.deepEqual(r.gaps.historicalForms,['Sint Nicolaas']);
});

test('obsolete terminology gap is detected',()=>{
 const r=searchLanguageGate({obsoleteTermsExpected:['old-name'],searchedObsoleteTerms:[]}).searchLanguage;
 assert.equal(r.gapCount,1);
});

test('complete declared coverage passes',()=>{
 const r=searchLanguageGate({relevantLanguages:['English','Dutch'],searchedLanguages:['English','Dutch'],historicalFormsExpected:['A','B'],searchedHistoricalForms:['A','B']}).searchLanguage;
 assert.equal(r.state,'language-coverage-characterized');
});

test('transliteration variants are separate search doors',()=>{
 const r=searchLanguageGate({transliterationsExpected:['Nikolaos','Nicholas'],searchedTransliterations:['Nicholas']}).searchLanguage;
 assert.deepEqual(r.gaps.transliterations,['Nikolaos']);
});
