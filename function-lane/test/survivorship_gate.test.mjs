import test from 'node:test';
import assert from 'node:assert/strict';
import { survivorshipGate } from '../core/survivorship_gate.mjs';

test('unsearched source class raises survivorship risk',()=>{
 const r=survivorshipGate({foundSources:8,expectedSourceClasses:['books','newspapers','manuscripts'],searchedSourceClasses:['books','newspapers']}).survivorship;
 assert.equal(r.state,'survivorship-risk');
 assert.deepEqual(r.unsearchedClasses,['manuscripts']);
});

test('known missing edition raises survivorship risk',()=>{
 const r=survivorshipGate({foundSources:5,expectedSourceClasses:['editions'],searchedSourceClasses:['editions'],missingKnownSources:['edition-1842']}).survivorship;
 assert.equal(r.state,'survivorship-risk');
});

test('complete characterized search can pass coverage gate',()=>{
 const r=survivorshipGate({foundSources:5,expectedSourceClasses:['books','archives'],searchedSourceClasses:['books','archives'],archiveSearchPerformed:true,contrarySearchPerformed:true}).survivorship;
 assert.equal(r.state,'coverage-characterized');
});

test('agreement without archive and contrary search remains limited',()=>{
 const r=survivorshipGate({foundSources:20,expectedSourceClasses:['web'],searchedSourceClasses:['web']}).survivorship;
 assert.equal(r.state,'coverage-limited');
});

test('no surviving evidence is not treated as proof of absence',()=>{
 const r=survivorshipGate({foundSources:0}).survivorship;
 assert.equal(r.state,'no-surviving-evidence-found');
});
