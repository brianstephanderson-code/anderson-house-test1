import test from 'node:test';
import assert from 'node:assert/strict';
import { confidenceCalibrationGate } from '../core/confidence_calibration_gate.mjs';

const base={contradictionSearch:true,contextFit:'yes',provenanceTraceable:true};

test('two independent clean roads earn strong',()=>{
 assert.equal(confidenceCalibrationGate({...base,independentRoads:2}).calibration.level,'strong');
});

test('one road is supported but not strong',()=>{
 assert.equal(confidenceCalibrationGate({...base,independentRoads:1}).calibration.level,'supported');
});

test('unresolved contradiction forces contested',()=>{
 assert.equal(confidenceCalibrationGate({...base,independentRoads:4,unresolvedContradictions:1}).calibration.level,'contested');
});

test('missing contradiction search stays unresolved despite many sources',()=>{
 assert.equal(confidenceCalibrationGate({...base,independentRoads:10,contradictionSearch:false}).calibration.level,'unresolved');
});

test('poor context fit cannot earn confidence',()=>{
 assert.equal(confidenceCalibrationGate({...base,independentRoads:5,contextFit:'no'}).calibration.level,'unresolved');
});
