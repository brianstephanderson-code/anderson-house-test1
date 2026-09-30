// WAREHOUSE RECHECK ROUTER
// Applies the Humility Gate to stored findings and returns only those
// that deserve another conveyor trip.

import { humilityGate } from './humility_gate.mjs';

export function warehouseRecheck(findings = [], change = {}) {
  const inspected = findings.map((item) => {
    const result = humilityGate({
      finding: item.finding ?? '',
      origin: item.origin ?? 'warehouse',
      evidencePassport: item.evidencePassport ?? null,
      logicTrace: item.logicTrace ?? [],
      newEvidence: Boolean(change.newEvidence),
      newTestFunction: Boolean(change.newTestFunction),
      contradiction: Boolean(item.contradiction || change.contradiction),
    }).humilityGate;
    return {...item, humility: result};
  });
  return {
    warehouseRecheck: {
      inspected,
      reopenBasket: inspected.filter((x) => x.humility.state === 'reopen'),
      recastBasket: inspected.filter((x) => x.humility.state === 'recast'),
      currentDone: inspected.filter((x) => x.humility.state === 'current-done'),
    },
  };
}
