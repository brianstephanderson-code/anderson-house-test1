// EVIDENCE POOL
// Store evidence once; parcels refer to it by stable evidence id.
// Shared research is allowed. Shared verdicts are not.

import { createHash } from 'node:crypto';

export function evidenceIdFor({ origin = '', claim = '', excerpt = '' } = {}) {
  return createHash('sha256').update(`${origin}\n${claim}\n${excerpt}`).digest('hex').slice(0,16);
}

export function addEvidence(pool = [], evidence = {}) {
  const item = {
    evidenceId: evidence.evidenceId ?? evidenceIdFor(evidence),
    origin: evidence.origin ?? '',
    sourceType: evidence.sourceType ?? 'unknown',
    claim: evidence.claim ?? '',
    excerpt: evidence.excerpt ?? '',
    provenance: evidence.provenance ?? [],
    context: evidence.context ?? '',
  };
  if (!item.origin || !item.claim) throw new Error('Evidence requires origin and claim');
  if (pool.some((x) => x.evidenceId === item.evidenceId)) return { pool, item, added: false };
  return { pool: [...pool, item], item, added: true };
}
