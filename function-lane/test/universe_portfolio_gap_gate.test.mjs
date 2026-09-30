import test from 'node:test';
import assert from 'node:assert/strict';
import {universePortfolioGapGate} from '../core/universe_portfolio_gap_gate.mjs';

test('repeated unresolved gap shape becomes portfolio blind spot',()=>{
 const r=universePortfolioGapGate({unresolvedGaps:[{id:'g1',signature:'physical-practice',triedUniverses:['semantic']},{id:'g2',signature:'physical-practice',triedUniverses:['semantic','historical']}]}).universePortfolioGap;
 assert.equal(r.blindSpots.length,1);
 assert.equal(r.state,'portfolio-blind-spots-found');
});

test('single unresolved gap does not overreact',()=>{
 const r=universePortfolioGapGate({unresolvedGaps:[{id:'g1',signature:'rare-one-off'}]}).universePortfolioGap;
 assert.equal(r.blindSpots.length,0);
});

test('failed universe history is preserved for discovery cast',()=>{
 const r=universePortfolioGapGate({unresolvedGaps:[{signature:'x',triedUniverses:['semantic']},{signature:'x',triedUniverses:['phonetic']}]}).universePortfolioGap;
 assert.deepEqual(r.blindSpots[0].failedUniverses,['semantic','phonetic']);
});

test('different gap shapes remain separate',()=>{
 const r=universePortfolioGapGate({unresolvedGaps:[{signature:'x'},{signature:'y'},{signature:'x'}]}).universePortfolioGap;
 assert.equal(r.blindSpots.length,1);
 assert.equal(r.blindSpots[0].signature,'x');
});

test('proven universe inventory is visible beside blind spots',()=>{
 const r=universePortfolioGapGate({provenUniverses:[{name:'semantic',proven:true},{name:'gesture',proven:false}],unresolvedGaps:[]}).universePortfolioGap;
 assert.equal(r.provenUniverseCount,1);
});
