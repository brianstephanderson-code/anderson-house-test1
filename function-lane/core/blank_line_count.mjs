export function blankLineResultFor(text = "") {
  const value = String(text);
  if (value.length === 0) return { blankLines: 0 };
  const lines = value.split(/\r\n|\r|\n/);
  return { blankLines: lines.filter((line) => line.trim().length === 0).length };
}
