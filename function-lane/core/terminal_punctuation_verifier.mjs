export function verifyTerminalPunctuation({ text = "", claimed = false } = {}) {
  const value = String(text).trim();
  const expected = value ? /[.!?]["'’”)]*$/u.test(value) : false;
  return {
    expected,
    claimed: Boolean(claimed),
    passed: expected === Boolean(claimed),
  };
}
