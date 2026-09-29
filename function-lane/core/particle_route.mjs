const ROUTES = Object.freeze({
  terminal_punctuation: Object.freeze({
    returnsTo: "text_profile",
    backupTo: "function_lane_checkpoint",
    crosstalk: Object.freeze(["terminal_punctuation_verifier"]),
  }),
  terminal_punctuation_verifier: Object.freeze({
    returnsTo: "terminal_punctuation",
    backupTo: "text_profile",
    crosstalk: Object.freeze([]),
  }),
});

export function routeFor(particle = "") {
  const route = ROUTES[String(particle)];
  if (!route) throw new Error(`Unknown particle: ${particle}`);
  return route;
}

export function uplinkFor(particle = "", { primaryAvailable = true } = {}) {
  const route = routeFor(particle);
  if (primaryAvailable) {
    return { via: "primary", to: route.returnsTo };
  }
  if (!route.backupTo) {
    throw new Error(`No backup uplink for: ${particle}`);
  }
  return { via: "backup", to: route.backupTo };
}

export function canCrosstalk(from = "", to = "") {
  return routeFor(from).crosstalk.includes(String(to));
}

export function crosstalkEnvelope(from = "", to = "", payload = null) {
  if (!canCrosstalk(from, to)) {
    throw new Error(`Crosstalk denied: ${from} -> ${to}`);
  }
  const route = routeFor(from);
  return {
    from: String(from),
    to: String(to),
    payload,
    returnTo: route.returnsTo,
    backupTo: route.backupTo,
  };
}
