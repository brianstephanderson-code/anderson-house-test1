// QUERY FRAMING GATE
// The wording of a search question selects an evidence universe.
// Cast more than one materially different query frame, including the function being performed in context.

export function queryFramingGate({
  target = '',
  purpose = '',
  context = '',
  queryFrames = [],
} = {}) {
  const kinds = new Set(queryFrames.map(q => q.kind).filter(Boolean));
  const required = ['name-or-definition','function-in-context','contrary-or-failure'];
  const missingFrames = required.filter(k => !kinds.has(k));
  const hasPurpose = Boolean(purpose);
  const hasContext = Boolean(context);

  let state = 'recast-query-frame';
  if (hasPurpose && hasContext && missingFrames.length === 0) state = 'multi-frame-ready';

  return {
    queryFraming: {
      target,
      purpose,
      context,
      state,
      frameKinds:[...kinds],
      missingFrames,
      rule:'SEARCH FOR THE FUNCTION, NOT MERELY THE NAME',
    },
  };
}
