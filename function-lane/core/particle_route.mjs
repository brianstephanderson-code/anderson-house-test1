const ROUTES = Object.freeze({
  terminal_punctuation: Object.freeze({
    returnsTo: "text_profile",
    crosstalk: Object.freeze(["terminal_punctuation_verifier"]),
  }),
  terminal_punctuation_verifier: Object.freeze({
    returnsTo: "terminal_punctuation",
    crosstalk: Object.freeze([]),
  }),
});

export function routeFor(particle = "") {
  const route = ROUTES[String(particle)];
  if (!route) throw new Error(`Unknown particle: ${particle}`);
  return route;
}

export function canCrosstalk(from = "", to = "") {
  return routeFor(from).crosstalk.includes(String(to));
}

export function crosstalkEnvelope(from = "", to = "", payload = null) {
  if (!canCrosstalk(from, to)) {
    throw new Error(`Crosstalk denied: ${from} -> ${to}`);
  }
  return {
    from: String(from),
    to: String(to),
    payload,
    returnTo: routeFor(from).returnsTo,
  };
}
