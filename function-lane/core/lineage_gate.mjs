// LINEAGE GATE
// A finished finding must be walkable backwards to the author's words.
// Keep evidence marriages, handoffs, decisions, uncertainty and rejected alternatives traceable.

export function lineageGate({
  finding = '',
  sourceTextRef = '',
  evidenceIds = [],
  marriageRefs = [],
  handoffRefs = [],
  decisionRefs = [],
  rejectedAlternatives = [],
  uncertainty = null,
} = {}) {
  const required = {
    finding: Boolean(finding),
    sourceTextRef: Boolean(sourceTextRef),
    evidence: Array.isArray(evidenceIds) && evidenceIds.length > 0,
    marriage: Array.isArray(marriageRefs) && marriageRefs.length > 0,
    handoff: Array.isArray(handoffRefs) && handoffRefs.length > 0,
    decision: Array.isArray(decisionRefs) && decisionRefs.length > 0,
  };
  const missing = Object.entries(required).filter(([,ok])=>!ok).map(([key])=>key);
  return {
    lineage: {
      state: missing.length ? 'return' : 'traceable',
      missing,
      finding,
      sourceTextRef,
      evidenceIds,
      marriageRefs,
      handoffRefs,
      decisionRefs,
      rejectedAlternatives,
      uncertainty,
      rule: 'DONE MUST BE WALKABLE BACK TO STATE',
    },
  };
}
