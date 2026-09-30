import test from 'node:test';
import assert from 'node:assert/strict';
import { authorityLaunderingGate } from '../core/authority_laundering_gate.mjs';

test('prestigious repetition without new evidence does not upgrade claim',()=>{
 const r=authorityLaunderingGate({sourceId:'major-reference',sourceAuthority:'high',claimOriginId:'old-note',presentedAsStrongerBecauseOfAuthority:true}).authorityLaundering;
 assert.equal(r.state,'authority-laundering-risk');
 assert.equal(r.addsSupport,false);
});

test('prestigious source can add support when it independently verifies',()=>{
 const r=authorityLaunderingGate({sourceId:'major-reference',sourceAuthority:'high',claimOriginId:'old-note',independentlyVerifiesClaim:true}).authorityLaundering;
 assert.equal(r.state,'new-support-added');
});

test('new independent evidence genuinely adds support',()=>{
 const r=authorityLaunderingGate({sourceId:'archive-study',claimOriginId:'old-note',addsIndependentEvidence:true}).authorityLaundering;
 assert.equal(r.state,'new-support-added');
});

test('ordinary repetition remains authority-neutral when not overstated',()=>{
 const r=authorityLaunderingGate({sourceId:'later-glossary',claimOriginId:'old-note'}).authorityLaundering;
 assert.equal(r.state,'authority-neutral');
});

test('unknown ancestry routes back to origin tracing',()=>{
 const r=authorityLaunderingGate({sourceId:'reference-X',sourceAuthority:'high'}).authorityLaundering;
 assert.equal(r.state,'trace-claim-origin');
});
