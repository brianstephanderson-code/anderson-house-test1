const NAME = /\b[A-Z][A-Za-z.'’-]+(?:\s+[A-Z][A-Za-z.'’-]+){1,2}\b/g;
const LONG_WORD = /\b[A-Za-z][A-Za-z'’-]{6,}\b/g;

export function candidateTokenResultFor(text = "") {
  const value = String(text);
  const namedReferences = [...new Set(value.match(NAME) ?? [])].sort();
  const wordCandidates = [...new Set((value.match(LONG_WORD) ?? []).map((word) => word.toLowerCase()))].sort();
  return { candidateTokens: { namedReferences, wordCandidates } };
}
