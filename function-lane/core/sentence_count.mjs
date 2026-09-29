export function countSentences(text = "") {
  const value = String(text).trim();
  if (!value) return 0;
  const matches = value.match(/[^.!?]+[.!?]+(?:["'’”)]*)|[^.!?]+$/gu);
  return matches ? matches.filter(part => part.trim()).length : 0;
}

export function sentenceResultFor(text = "") {
  return { sentences: countSentences(text) };
}
