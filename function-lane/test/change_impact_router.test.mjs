import test from 'node:test';
import assert from 'node:assert/strict';
import { routeChangeImpact } from '../core/change_impact_router.mjs';

const findings=[
 {finding:'A',lineage:{sourceTextRef:'p1',evidenceIds:['ev1'],handoffRefs:['meaning-fit','verify']}},
 {finding:'B',lineage:{sourceTextRef:'p2',evidenceIds:['ev2'],handoffRefs:['place-fit','verify']}},
];

test('changed evidence reopens only dependent finding',()=>{
 const r=routeChangeImpact(findings,{evidenceIds:['ev1']}).changeImpact;
 assert.deepEqual(r.affected.map(x=>x.finding),['A']);
 assert.deepEqual(r.untouched.map(x=>x.finding),['B']);
});

test('changed function reaches all findings that used it',()=>{
 const r=routeChangeImpact(findings,{functionRefs:['verify']}).changeImpact;
 assert.equal(r.affected.length,2);
});

test('source correction reaches only matching source lineage',()=>{
 const r=routeChangeImpact(findings,{sourceTextRefs:['p2']}).changeImpact;
 assert.deepEqual(r.affected.map(x=>x.finding),['B']);
});

test('unrelated change leaves warehouse alone',()=>{
 const r=routeChangeImpact(findings,{evidenceIds:['ev99']}).changeImpact;
 assert.equal(r.affected.length,0);
 assert.equal(r.untouched.length,2);
});
