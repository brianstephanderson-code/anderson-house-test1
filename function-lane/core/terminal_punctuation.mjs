export function hasTerminalPunctuation(text = "") {
  const value = String(text).trim();
  return value ? /[.!?]["'’”)]*$/u.test(value) : false;
}

export function punctuationResultFor(text = "") {
  return { terminalPunctuation: hasTerminalPunctuation(text) };
}
