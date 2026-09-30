import test from 'node:test';
import assert from 'node:assert/strict';
import { geographyFitGate } from '../core/geography_fit_gate.mjs';

test('matching region and community pass',()=>{
 const r=geographyFitGate({targetRegion:'Hudson Valley',targetCommunity:'Dutch-American',evidenceRegion:'Hudson Valley',evidenceCommunity:'Dutch-American'}).geographyFit;
 assert.equal(r.state,'geography-fit');
});

test('foreign definition alone requires local recast',()=>{
 const r=geographyFitGate({targetRegion:'New York',evidenceRegion:'Britain'}).geographyFit;
 assert.equal(r.state,'recast-local-evidence');
});

test('known regional difference raises mismatch risk',()=>{
 const r=geographyFitGate({targetRegion:'New York',evidenceRegion:'Britain',regionalDifferenceKnown:true}).geographyFit;
 assert.equal(r.state,'regional-mismatch-risk');
});

test('same sense can be bridged across regions with evidence',()=>{
 const r=geographyFitGate({targetRegion:'New York',evidenceRegion:'Britain',sameSenseAcrossRegionsDemonstrated:true}).geographyFit;
 assert.equal(r.state,'sense-bridged-across-regions');
});

test('explicit local usage verification passes despite broad source label',()=>{
 const r=geographyFitGate({targetRegion:'Hudson Valley',evidenceRegion:'United States',localUsageVerified:true}).geographyFit;
 assert.equal(r.state,'geography-fit');
});
