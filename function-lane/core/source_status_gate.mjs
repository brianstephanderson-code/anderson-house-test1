// SOURCE STATUS GATE
// Do not confuse 'oldest source we found' with 'primary source'.
// Primary status must be positively established by relation to the event/claim/work.

export function sourceStatusGate({
  sourceId = '',
  claimedStatus = 'unknown',
  directRelation = false,
  creatorOrWitness = false,
  originalRecord = false,
  derivesFromEarlier = null,
  earlierSearchPerformed = false,
  earlierSourceFound = false,
} = {}) {
  let status = 'unresolved';

  const positivePrimary = directRelation && (creatorOrWitness || originalRecord) && derivesFromEarlier !== true;
  if (positivePrimary) status = 'primary-established';
  else if (earlierSourceFound || derivesFromEarlier === true) status = 'secondary-or-derived';
  else if (earlierSearchPerformed) status = 'earliest-known-not-primary-proven';

  return {
    sourceStatus: {
      sourceId,
      claimedStatus,
      status,
      primaryEstablished: status === 'primary-established',
      rule: 'OLDEST FOUND IS NOT THE SAME AS PRIMARY',
    },
  };
}
