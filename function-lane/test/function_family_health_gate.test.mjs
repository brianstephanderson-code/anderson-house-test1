import test from 'node:test';
import assert from 'node:assert/strict';
import {functionFamilyHealthGate} from '../core/function_family_health_gate.mjs';

const good={completed:true,holeClosed:true,contextPreserved:true,provenancePreserved:true,extraAssumptions:false};
const bad={...good,holeClosed:false};

test('healthy parent and child remain active',()=>{
 const r=functionFamilyHealthGate({members:[{functionId:'parent',uses:[good,good,good]},{functionId:'child',uses:[good,good,good]}]}).functionFamilyHealth;
 assert.equal(r.degraded.length,0);
});

test('sick child is quarantined without stopping healthy parent',()=>{
 const r=functionFamilyHealthGate({members:[{functionId:'parent',uses:[good,good,good]},{functionId:'child',uses:[bad,bad,good]}]}).functionFamilyHealth;
 assert.deepEqual(r.degraded,['child']);
 assert.equal(r.familyAction,'keep-healthy-members-working');
});

test('sick parent does not automatically condemn healthy child',()=>{
 const r=functionFamilyHealthGate({members:[{functionId:'parent',uses:[bad,bad,good]},{functionId:'child',uses:[good,good,good]}]}).functionFamilyHealth;
 assert.deepEqual(r.healthy,['child']);
});

test('hidden assumptions count as member failure',()=>{
 const sneaky={...good,extraAssumptions:true};
 const r=functionFamilyHealthGate({members:[{functionId:'child',uses:[sneaky,sneaky,good]}]}).functionFamilyHealth;
 assert.deepEqual(r.degraded,['child']);
});

test('if nobody is healthy family recovery opens',()=>{
 const r=functionFamilyHealthGate({members:[{functionId:'parent',uses:[bad,bad,bad]},{functionId:'child',uses:[bad,bad,bad]}]}).functionFamilyHealth;
 assert.equal(r.familyAction,'open-family-recovery');
});
