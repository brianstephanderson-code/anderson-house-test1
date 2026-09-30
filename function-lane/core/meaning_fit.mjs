// MEANING FIT
// Function-first verification for glossary candidates.
// It does not invent a definition. It compares supplied candidate meanings
// against the local communication job and records what still needs evidence.

export function meaningFit({ term, context, candidateMeanings = [] } = {}) {
  if (!term || !context) throw new Error('term and context are required');

  return {
    meaningFit: {
      term,
      context,
      question: `What function does "${term}" perform in this context?`,
      candidateMeanings: candidateMeanings.map((meaning) => ({
        meaning,
        status: 'unverified',
        tests: {
          sentenceFunctionFit: 'pending',
          widerContextFit: 'pending',
          externalEvidenceFit: 'pending',
        },
      })),
      allowedDoneStates: [
        'verified-contextual-meaning',
        'multiple-functions',
        'uncertain-recast',
        'error-or-artifact',
        'no-material-function',
      ],
      rule: 'FUNCTION FIRST; DEVICE AND DICTIONARY POSITION SECOND',
    },
  };
}
