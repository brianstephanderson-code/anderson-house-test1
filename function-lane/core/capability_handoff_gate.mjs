// CAPABILITY HANDOFF GATE
// Composed bees are only useful if the parcel survives each handoff intact.
// Verify STATE, evidence, context and expected next capability at every joint.

export function capabilityHandoffGate({handoffs=[]}={}) {
  const accepted=[];
  const blocked=[];
  for (const h of handoffs) {
    const checks={
      statePreserved:h.statePreserved===true,
      evidencePreserved:h.evidencePreserved===true,
      contextPreserved:h.contextPreserved===true,
      nextCapabilityMatches:h.nextCapabilityMatches===true
    };
    const clean=Object.values(checks).every(Boolean);
    (clean?accepted:blocked).push({...h,checks});
  }
  return {
    capabilityHandoff:{
      accepted,blocked,
      state:blocked.length?'handoff-repair-required':'handoffs-clean',
      rule:'COMPOSE THE BEES, BUT VERIFY EVERY JOINT; THE PARCEL MUST SURVIVE THE HANDOFF'
    }
  };
}
