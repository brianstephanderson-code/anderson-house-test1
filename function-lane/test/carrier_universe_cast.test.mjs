import test from 'node:test';
import assert from 'node:assert/strict';
import {carrierUniverseCast} from '../core/carrier_universe_cast.mjs';

test('opens multiple carrier universes before meadow selection',()=>{
 const r=carrierUniverseCast({purpose:'recover old fishing knowledge',unknown:'how method worked',candidateCarriers:['document','people','practice','object','place','environment']}).carrierCast;
 assert.equal(r.state,'universes-open');
 assert.ok(r.carriers.includes('practice'));
});

test('web is not required as a carrier universe',()=>{
 const r=carrierUniverseCast({purpose:'find evidence',unknown:'old technique',candidateCarriers:['people','object']}).carrierCast;
 assert.equal(r.state,'universes-open');
});

test('duplicate carrier ideas collapse',()=>{
 const r=carrierUniverseCast({purpose:'x',unknown:'y',candidateCarriers:['place','place']}).carrierCast;
 assert.deepEqual(r.carriers,['place']);
});

test('empty carrier cast is recast rather than silently defaulted',()=>{
 const r=carrierUniverseCast({purpose:'x',unknown:'y'}).carrierCast;
 assert.equal(r.state,'recast-carriers');
});

test('unexplored universes remain visible for recursive recast',()=>{
 const r=carrierUniverseCast({purpose:'x',unknown:'y',candidateCarriers:['document']}).carrierCast;
 assert.ok(r.unexplored.includes('people'));
 assert.ok(r.unexplored.includes('environment'));
});
