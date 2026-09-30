import test from 'node:test';
import assert from 'node:assert/strict';
import {missingUniversePredictionGate} from '../core/missing_universe_prediction_gate.mjs';

const base={
 explanation:'method depended on darkness',
 sourceUniverses:['document','people'],
 targetUniverse:'environment',
 predictedObservation:'conditions should make the method more effective at night',
 predictionRecordedBeforeSearch:true,
};

test('complete pre-search prediction is ready',()=>{
 const r=missingUniversePredictionGate(base).missingUniversePrediction;
 assert.equal(r.state,'prediction-ready');
});

test('matching independent observation records prediction met',()=>{
 const r=missingUniversePredictionGate({...base,observed:true}).missingUniversePrediction;
 assert.equal(r.state,'prediction-met');
});

test('failed prediction forces recast rather than being hidden',()=>{
 const r=missingUniversePredictionGate({...base,observed:false}).missingUniversePrediction;
 assert.equal(r.state,'prediction-failed-recast');
});

test('prediction written after searching cannot pass as prediction',()=>{
 const r=missingUniversePredictionGate({...base,predictionRecordedBeforeSearch:false,observed:true}).missingUniversePrediction;
 assert.equal(r.state,'form-prediction');
});

test('missing target universe cannot pass',()=>{
 const r=missingUniversePredictionGate({...base,targetUniverse:''}).missingUniversePrediction;
 assert.equal(r.state,'form-prediction');
});
