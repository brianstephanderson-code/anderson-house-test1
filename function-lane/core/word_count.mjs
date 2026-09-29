export function countWords(text = "") {
  const value = String(text).trim();
  return value ? value.split(/\s+/u).length : 0;
}

export function resultFor(text = "") {
  return { words: countWords(text) };
}
