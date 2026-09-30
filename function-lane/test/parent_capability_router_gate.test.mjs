import test from 'node:test';
import assert from 'node:assert/strict';
import {parentCapabilityRouterGate} from '../core/parent_capability_router_gate.mjs';

const cap={functionId:'nonwritten-carrier',satisfies:['preserve-nonwritten-transmission'],signatureFamily:['oral','gesture','demonstration'],available:true,proof:{distinct:3},provenance:['trial-set']};

test('matching new hole routes to proven parent capability',()=>{
 const r=parentCapabilityRouterGate({hole:{id:'h1',signature:'gesture',requirements:['preserve-nonwritten-transmission']},capabilities:[cap]}).parentCapabilityRouter;
 assert.equal(r.routes[0].functionId,'nonwritten-carrier');
});

test('wrong signature family prevents forced reuse',()=>{
 const r=parentCapabilityRouterGate({hole:{signature:'database',requirements:['preserve-nonwritten-transmission']},capabilities:[cap]}).parentCapabilityRouter;
 assert.equal(r.routes.length,0);
});

test('missing required function prevents route',()=>{
 const r=parentCapabilityRouterGate({hole:{signature:'oral',requirements:['preserve-time-order']},capabilities:[cap]}).parentCapabilityRouter;
 assert.equal(r.state,'return-hole-to-function-discovery');
});

test('unavailable parent capability cannot receive work',()=>{
 const r=parentCapabilityRouterGate({hole:{signature:'oral',requirements:['preserve-nonwritten-transmission']},capabilities:[{...cap,available:false}]}).parentCapabilityRouter;
 assert.equal(r.routes.length,0);
});

test('several fitting parent capabilities remain candidates rather than forced winner',()=>{
 const r=parentCapabilityRouterGate({hole:{signature:'oral',requirements:['preserve-nonwritten-transmission']},capabilities:[cap,{...cap,functionId:'carrier-2'}]}).parentCapabilityRouter;
 assert.equal(r.routes.length,2);
 assert.equal(r.selection,null);
});
