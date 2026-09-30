import test from 'node:test';
import assert from 'node:assert/strict';
import {functionFamilyFailoverGate} from '../core/function_family_failover_gate.mjs';

const member=(id,health='healthy')=>({functionId:id,proven:true,available:true,health,satisfies:['preserve'],signatures:['oral']});
const job={id:'j1',signature:'oral',requirements:['preserve']};

test('healthy preferred function keeps job',()=>{
 const r=functionFamilyFailoverGate({job,preferredFunction:'a',members:[member('a'),member('b')]}).functionFamilyFailover;
 assert.equal(r.route,'a');
 assert.equal(r.mode,'preferred');
});

test('degraded preferred function fails over to healthy proven fit',()=>{
 const r=functionFamilyFailoverGate({job,preferredFunction:'a',members:[member('a','degraded'),member('b')]}).functionFamilyFailover;
 assert.equal(r.route,'b');
 assert.equal(r.mode,'failover');
});

test('unavailable preferred function fails over',()=>{
 const a={...member('a'),available:false};
 const r=functionFamilyFailoverGate({job,preferredFunction:'a',members:[a,member('b')]}).functionFamilyFailover;
 assert.equal(r.route,'b');
});

test('multiple healthy alternates remain candidates instead of arbitrary winner',()=>{
 const r=functionFamilyFailoverGate({job,preferredFunction:'a',members:[member('a','degraded'),member('b'),member('c')]}).functionFamilyFailover;
 assert.equal(r.route,null);
 assert.deepEqual(r.candidates,['b','c']);
});

test('no proven fit preserves job and opens discovery',()=>{
 const r=functionFamilyFailoverGate({job,preferredFunction:'a',members:[member('a','degraded')]}).functionFamilyFailover;
 assert.equal(r.state,'hold-job-and-open-discovery');
});
