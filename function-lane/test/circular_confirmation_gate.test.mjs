import test from 'node:test';
import assert from 'node:assert/strict';
import { circularConfirmationGate } from '../core/circular_confirmation_gate.mjs';

test('A to B to C to A is detected as circular',()=>{
 const r=circularConfirmationGate([{from:'A',to:'B'},{from:'B',to:'C'},{from:'C',to:'A'}]).circularConfirmation;
 assert.equal(r.state,'circular-evidence');
 assert.equal(r.cycles.length,1);
});

test('straight chain to primary source is clear',()=>{
 const r=circularConfirmationGate([{from:'A',to:'B'},{from:'B',to:'PRIMARY'}]).circularConfirmation;
 assert.equal(r.state,'clear');
});

test('self citation is a loop',()=>{
 const r=circularConfirmationGate([{from:'A',to:'A'}]).circularConfirmation;
 assert.equal(r.state,'circular-evidence');
});

test('loop is found inside otherwise useful graph',()=>{
 const r=circularConfirmationGate([
  {from:'A',to:'PRIMARY'},
  {from:'B',to:'C'},
  {from:'C',to:'B'},
 ]).circularConfirmation;
 assert.equal(r.state,'circular-evidence');
 assert.ok(r.members.includes('B'));
 assert.ok(r.members.includes('C'));
});
