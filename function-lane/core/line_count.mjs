export function lineResultFor(text = "") {
  const value = String(text);
  if (value.length === 0) return { lines: 0 };
  return { lines: value.split(/\r\n|\r|\n/).length };
}
