// EVIDENCE MARRIAGE CLERK
// Tests whether pooled evidence supports one particular parcel.
// Never infers a verdict merely because evidence was shared with a batch.

export function marryEvidence({ parcel = {}, evidence = {}, claimSupport = 'pending', contextFit = 'pending' } = {}) {
  const accepted = claimSupport === 'yes' && contextFit === 'yes';
  const rejected = claimSupport === 'no' || contextFit === 'no';
  return {
    marriage: {
      parcelTerm: parcel.term ?? '',
      evidenceId: evidence.evidenceId ?? '',
      claimSupport,
      contextFit,
      state: accepted ? 'matched' : rejected ? 'rejected' : 'pending',
      rule: 'SHARE THE RESEARCH; NEVER SHARE THE VERDICT',
    },
  };
}
