// CHANGE IMPACT ROUTER
// When evidence or a function changes, use lineage to reopen only findings that depend on it.
// This turns lineage from an audit trail into active factory plumbing.

function intersects(a = [], b = []) {
  const wanted = new Set(b);
  return a.some((x) => wanted.has(x));
}

export function routeChangeImpact(findings = [], change = {}) {
  const changedEvidenceIds = change.evidenceIds ?? [];
  const changedFunctionRefs = change.functionRefs ?? [];
  const changedSourceTextRefs = change.sourceTextRefs ?? [];

  const inspected = findings.map((item) => {
    const lineage = item.lineage ?? {};
    const reasons = [];
    if (intersects(lineage.evidenceIds ?? [], changedEvidenceIds)) reasons.push('evidence-changed');
    if (intersects(lineage.handoffRefs ?? [], changedFunctionRefs)) reasons.push('function-or-handoff-changed');
    if (changedSourceTextRefs.includes(lineage.sourceTextRef)) reasons.push('source-text-changed');
    return {...item, impact:{affected:reasons.length>0,reasons}};
  });

  return {
    changeImpact: {
      affected: inspected.filter((x)=>x.impact.affected),
      untouched: inspected.filter((x)=>!x.impact.affected),
    },
  };
}
