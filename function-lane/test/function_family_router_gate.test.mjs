import test from 'node:test';
import assert from 'node:assert/strict';
import {functionFamilyRouterGate} from '../core/function_family_router_gate.mjs';

const parent={functionId:'carrier',proven:true,available:true,satisfies:['preserve'],signatures:['oral','gesture']};
const child={functionId:'database-carrier',proven:true,available:true,satisfies:['preserve'],signatures:['database']};

test('specialist child receives matching boundary work',()=>{
 const r=functionFamilyRouterGate({hole:{id:'h1',signature:'database',requirements:['preserve']},parent,children:[child]}).functionFamilyRouter;
 assert.equal(r.routes[0].functionId,'database-carrier');
});

test('healthy parent keeps work in its proven territory',()=>{
 const r=functionFamilyRouterGate({hole:{signature:'oral',requirements:['preserve']},parent,children:[child]}).functionFamilyRouter;
 assert.equal(r.routes[0].functionId,'carrier');
});

test('unproven child cannot steal work from discovery',()=>{
 const r=functionFamilyRouterGate({hole:{signature:'database',requirements:['preserve']},parent,children:[{...child,proven:false}]}).functionFamilyRouter;
 assert.equal(r.state,'return-hole-to-discovery');
});

test('multiple specialist children remain parallel route candidates',()=>{
 const r=functionFamilyRouterGate({hole:{signature:'database',requirements:['preserve']},parent,children:[child,{...child,functionId:'database-carrier-2'}]}).functionFamilyRouter;
 assert.equal(r.routes.length,2);
 assert.equal(r.selection,null);
});

test('no family fit returns hole to discovery',()=>{
 const r=functionFamilyRouterGate({hole:{signature:'music',requirements:['preserve']},parent,children:[child]}).functionFamilyRouter;
 assert.equal(r.routes.length,0);
});
