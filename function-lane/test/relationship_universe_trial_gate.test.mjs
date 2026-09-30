import test from 'node:test';
import assert from 'node:assert/strict';
import {relationshipUniverseTrialGate} from '../core/relationship_universe_trial_gate.mjs';

const good=id=>({completed:true,gapId:id,bridgeFound:true,relationRuleApplied:true,contextPreserved:true,provenancePresent:true,extraAssumptions:false});

test('new universe qualifies after clean trials across distinct gaps',()=>{
 const r=relationshipUniverseTrialGate({universe:{name:'gesture'},trials:[good('g1'),good('g2'),good('g3')]}).relationshipUniverseTrial;
 assert.equal(r.state,'relationship-universe-proven');
 assert.equal(r.action,'add-to-universe-pool');
});

test('one clever success does not create a universe',()=>{
 const r=relationshipUniverseTrialGate({universe:{name:'gesture'},trials:[good('g1')]}).relationshipUniverseTrial;
 assert.equal(r.state,'relationship-universe-unproven');
});

test('repeating same gap does not fake generality',()=>{
 const r=relationshipUniverseTrialGate({universe:{name:'gesture'},trials:[good('g1'),good('g1'),good('g1')]}).relationshipUniverseTrial;
 assert.equal(r.distinctCleanGaps,1);
 assert.equal(r.state,'relationship-universe-unproven');
});

test('missing provenance prevents clean universe trial',()=>{
 const r=relationshipUniverseTrialGate({universe:{name:'gesture'},trials:[good('g1'),good('g2'),{...good('g3'),provenancePresent:false}]}).relationshipUniverseTrial;
 assert.equal(r.cleanTrials,2);
});

test('hidden assumptions prevent universe qualification',()=>{
 const r=relationshipUniverseTrialGate({universe:{name:'gesture'},trials:[good('g1'),good('g2'),{...good('g3'),extraAssumptions:true}]}).relationshipUniverseTrial;
 assert.equal(r.state,'relationship-universe-unproven');
});
