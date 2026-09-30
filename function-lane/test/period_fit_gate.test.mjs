import test from 'node:test';
import assert from 'node:assert/strict';
import { periodFitGate } from '../core/period_fit_gate.mjs';

test('verified period usage passes',()=>{
 const r=periodFitGate({authorYear:1820,evidenceYear:1818,periodUsageVerified:true}).periodFit;
 assert.equal(r.state,'period-fit');
});

test('modern definition alone requires period recast',()=>{
 const r=periodFitGate({authorYear:1820,evidenceYear:1950}).periodFit;
 assert.equal(r.state,'recast-period-evidence');
 assert.equal(r.distanceYears,130);
});

test('known semantic shift raises mismatch risk',()=>{
 const r=periodFitGate({authorYear:1820,evidenceYear:1950,semanticShiftKnown:true}).periodFit;
 assert.equal(r.state,'period-mismatch-risk');
});

test('later evidence can be used when same sense is independently bridged',()=>{
 const r=periodFitGate({authorYear:1820,evidenceYear:1950,sameSenseDemonstrated:true}).periodFit;
 assert.equal(r.state,'sense-bridged-across-time');
});

test('missing dates do not silently pass',()=>{
 const r=periodFitGate({}).periodFit;
 assert.equal(r.state,'recast-period-evidence');
});
