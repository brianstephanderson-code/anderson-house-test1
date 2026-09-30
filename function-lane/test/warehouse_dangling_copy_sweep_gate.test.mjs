import test from 'node:test';
import assert from 'node:assert/strict';
import {warehouseDanglingCopySweepGate} from '../core/warehouse_dangling_copy_sweep_gate.mjs';

test('copy closes after job loop and evidence are safe',()=>{
 const r=warehouseDanglingCopySweepGate({copies:[{copyId:'c1',jobId:'j1',evidence:['e1']}],closedJobIds:['j1'],preservedEvidence:['e1']}).warehouseDanglingCopySweep;
 assert.deepEqual(r.close,['c1']);
 assert.equal(r.state,'copy-loops-clean');
});

test('copy stays when original job loop is open',()=>{
 const r=warehouseDanglingCopySweepGate({copies:[{copyId:'c1',jobId:'j1'}],closedJobIds:[]}).warehouseDanglingCopySweep;
 assert.equal(r.hold[0].reason,'job-loop-open');
});

test('copy stays when its evidence is not yet preserved',()=>{
 const r=warehouseDanglingCopySweepGate({copies:[{copyId:'c1',jobId:'j1',evidence:['e2']}],closedJobIds:['j1'],preservedEvidence:['e1']}).warehouseDanglingCopySweep;
 assert.equal(r.hold[0].reason,'evidence-not-preserved');
});

test('safe copies close while unsafe copies remain held',()=>{
 const r=warehouseDanglingCopySweepGate({copies:[{copyId:'c1',jobId:'j1'},{copyId:'c2',jobId:'j2'}],closedJobIds:['j1']}).warehouseDanglingCopySweep;
 assert.deepEqual(r.close,['c1']);
 assert.equal(r.hold[0].copyId,'c2');
});

test('no copies means clean basket',()=>{
 const r=warehouseDanglingCopySweepGate({copies:[],closedJobIds:[]}).warehouseDanglingCopySweep;
 assert.equal(r.state,'copy-loops-clean');
});
