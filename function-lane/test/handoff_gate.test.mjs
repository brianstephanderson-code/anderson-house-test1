import test from 'node:test';
import assert from 'node:assert/strict';
import { handoffGate } from '../core/handoff_gate.mjs';

const base={stateIn:'researched',resultOut:'candidate meaning',nextFunction:'verification',sufficient:true};

test('complete atomic parcel is accepted',()=>{
  assert.equal(handoffGate({parcel:base}).handoff.state,'accept');
});

test('uncertainty lost during handoff is returned',()=>{
  const p={...base,hadUncertainty:true,uncertainty:''};
  const r=handoffGate({parcel:p}).handoff;
  assert.equal(r.state,'return');
  assert.equal(r.informationLoss.uncertaintyLost,true);
});

test('provenance lost during handoff is returned',()=>{
  const p={...base,hadProvenance:true,provenance:[]};
  assert.equal(handoffGate({parcel:p}).handoff.state,'return');
});

test('multiple independent claims request split',()=>{
  const p={...base,claims:['claim A','claim B']};
  assert.equal(handoffGate({parcel:p}).handoff.state,'split');
});

test('insufficient but intact parcel is recast',()=>{
  const p={...base,sufficient:false};
  assert.equal(handoffGate({parcel:p}).handoff.state,'recast');
});
