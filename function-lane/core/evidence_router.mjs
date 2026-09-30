// EVIDENCE ROUTER
// Decides what KIND of evidence door a Meaning Fit parcel needs before a cast.
// It does not decide the meaning itself.

export function routeEvidence(parcel = {}) {
  const term = String(parcel.term ?? '').trim();
  const context = String(parcel.context ?? '');
  if (!term || !context) throw new Error('term and context are required');

  const looksNamed = /^(?:[A-Z][\w.'’-]*)(?:\s+[A-Z][\w.'’-]*)+$/.test(term);
  const looksAbbrev = /\b[A-Z][a-z]?\./.test(term);

  const doors = looksNamed || looksAbbrev
    ? ['local-context', 'reference-identity', 'historical-context']
    : ['local-context', 'historical-dictionary', 'usage-evidence'];

  return {
    evidenceRoute: {
      term,
      doors,
      state: 'needs-evidence',
      rule: 'ROUTE BY REQUIRED EVIDENCE FUNCTION; DO NOT INFER MEANING FROM SHAPE',
    },
  };
}
