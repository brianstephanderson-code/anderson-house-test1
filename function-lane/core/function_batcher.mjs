// FUNCTION BATCHER
// Groups Meaning Fit parcels by the kind of function/evidence question they need.
// This reduces repeated casts without deciding meaning prematurely.

export function batchByFunction({ glossaryParcels = [], namedParcels = [] } = {}) {
  const batches = {
    namedReferenceFunction: namedParcels,
    lexicalMeaningFunction: glossaryParcels,
  };

  return {
    functionBatches: Object.entries(batches)
      .filter(([, parcels]) => parcels.length)
      .map(([functionClass, parcels]) => ({
        functionClass,
        count: parcels.length,
        parcels,
        sharedQuestion:
          functionClass === 'namedReferenceFunction'
            ? 'What does this named reference identify here, and what function does it perform in the communication?'
            : 'What meaning/function does this term have here, and which candidate meaning fits the sentence and wider context?',
        rule: 'BATCH THE CAST; VERIFY EACH RETURN AGAINST ITS OWN CONTEXT',
      })),
  };
}
