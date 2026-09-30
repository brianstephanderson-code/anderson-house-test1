import test from 'node:test';
import assert from 'node:assert/strict';
import { queryFramingGate } from '../core/query_framing_gate.mjs';

const frames=[
 {kind:'name-or-definition',q:'What does Saint Nicholas mean?'},
 {kind:'function-in-context',q:'What function is Saint Nicholas performing in this sentence?'},
 {kind:'contrary-or-failure',q:'Where does this interpretation fail or differ?'},
];

test('definition plus function plus contrary frames are ready',()=>{
 const r=queryFramingGate({target:'Saint Nicholas',purpose:'reader glossary',context:'sentence-12',queryFrames:frames}).queryFraming;
 assert.equal(r.state,'multi-frame-ready');
});

test('definition-only search is insufficient',()=>{
 const r=queryFramingGate({target:'Saint Nicholas',purpose:'reader glossary',context:'sentence-12',queryFrames:[frames[0]]}).queryFraming;
 assert.equal(r.state,'recast-query-frame');
 assert.ok(r.missingFrames.includes('function-in-context'));
});

test('function frame alone still needs contrary cast',()=>{
 const r=queryFramingGate({target:'X',purpose:'meaning',context:'sentence',queryFrames:[frames[0],frames[1]]}).queryFraming;
 assert.ok(r.missingFrames.includes('contrary-or-failure'));
});

test('missing passage context cannot pass',()=>{
 const r=queryFramingGate({target:'X',purpose:'meaning',queryFrames:frames}).queryFraming;
 assert.equal(r.state,'recast-query-frame');
});

test('missing purpose cannot pass',()=>{
 const r=queryFramingGate({target:'X',context:'sentence',queryFrames:frames}).queryFraming;
 assert.equal(r.state,'recast-query-frame');
});
