// INDEPENDENCE GATE
// Count origins, not echoes. Multiple pages repeating one underlying source are one evidence family.

export function independenceGate(sources = []) {
  const families = new Map();
  const unresolved = [];

  for (const source of sources) {
    const id = source.id ?? source.url ?? source.name ?? 'unknown';
    const origin = source.originId ?? source.primarySourceId ?? null;
    if (!origin) {
      unresolved.push(id);
      continue;
    }
    if (!families.has(origin)) families.set(origin, []);
    families.get(origin).push(id);
  }

  const evidenceFamilies = [...families.entries()].map(([originId,members])=>({originId,members}));
  return {
    independence: {
      sourceCount: sources.length,
      independentRoads: evidenceFamilies.length,
      evidenceFamilies,
      unresolvedOrigins: unresolved,
      state: unresolved.length ? 'trace-origins' : 'ready',
      rule: 'COUNT ORIGINS, NOT ECHOES',
    },
  };
}
