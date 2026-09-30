import test from 'node:test';
import assert from 'node:assert/strict';
import {blindSpotClusterGate} from '../core/blind_spot_cluster_gate.mjs';

test('different surface gaps with same unmet function become one cluster',()=>{
 const r=blindSpotClusterGate({blindSpots:[
  {signature:'oral-practice',unmetRequirements:['preserve-nonwritten-transmission'],examples:['g1'],count:2},
  {signature:'gesture-practice',unmetRequirements:['preserve-nonwritten-transmission'],examples:['g2'],count:3}
 ]}).blindSpotCluster;
 assert.equal(r.clusters.length,1);
 assert.equal(r.clusters[0].count,5);
});

test('different unmet functions remain separate clusters',()=>{
 const r=blindSpotClusterGate({blindSpots:[
  {signature:'x',unmetRequirements:['time-sequence']},
  {signature:'y',unmetRequirements:['physical-location']}
 ]}).blindSpotCluster;
 assert.equal(r.clusters.length,2);
});

test('requirement order does not split identical deeper hole',()=>{
 const r=blindSpotClusterGate({blindSpots:[
  {signature:'x',unmetRequirements:['context','provenance']},
  {signature:'y',unmetRequirements:['provenance','context']}
 ]}).blindSpotCluster;
 assert.equal(r.clusters.length,1);
});

test('cluster preserves all surface signatures for traceability',()=>{
 const r=blindSpotClusterGate({blindSpots:[
  {signature:'x',unmetRequirements:['same']},{signature:'y',unmetRequirements:['same']}
 ]}).blindSpotCluster;
 assert.deepEqual(r.clusters[0].signatures,['x','y']);
});

test('no blind spots produces no fake deeper pattern',()=>{
 const r=blindSpotClusterGate({blindSpots:[]}).blindSpotCluster;
 assert.equal(r.state,'no-blind-spots-to-cluster');
});
