import { crosstalkEnvelope, routeFor } from "./particle_route.mjs";
import { verifyTerminalPunctuation } from "./terminal_punctuation_verifier.mjs";

export function hasTerminalPunctuation(text = "") {
  const value = String(text).trim();
  return value ? /[.!?]["'’”)]*$/u.test(value) : false;
}

export function punctuationResultFor(text = "") {
  const terminalPunctuation = hasTerminalPunctuation(text);

  const message = crosstalkEnvelope(
    "terminal_punctuation",
    "terminal_punctuation_verifier",
    { text: String(text), claimed: terminalPunctuation },
  );

  const verification = verifyTerminalPunctuation(message.payload);

  return {
    terminalPunctuation,
    particleRoute: {
      particle: "terminal_punctuation",
      ...routeFor("terminal_punctuation"),
    },
    crosstalkVerification: {
      by: message.to,
      returnTo: message.returnTo,
      passed: verification.passed,
    },
  };
}
