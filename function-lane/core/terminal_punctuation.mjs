import { routeFor } from "./particle_route.mjs";

export function hasTerminalPunctuation(text = "") {
  const value = String(text).trim();
  return value ? /[.!?]["'’”)]*$/u.test(value) : false;
}

export function punctuationResultFor(text = "") {
  return {
    terminalPunctuation: hasTerminalPunctuation(text),
    particleRoute: {
      particle: "terminal_punctuation",
      ...routeFor("terminal_punctuation"),
    },
  };
}
