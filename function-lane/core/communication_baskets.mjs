const BASKETS = Object.freeze({
  ORDERS: Object.freeze({ direction: "down", managementVisible: true }),
  CROSSTALK: Object.freeze({ direction: "sideways", managementVisible: false }),
  UPLINK: Object.freeze({ direction: "up", managementVisible: true }),
});

export function basketFor(channel = "") {
  const key = String(channel).toUpperCase();
  const basket = BASKETS[key];
  if (!basket) throw new Error(`Unknown communication channel: ${channel}`);
  return { channel: key, ...basket };
}

export function managementShouldWatch(channel = "") {
  return basketFor(channel).managementVisible;
}

export function promoteCrosstalk({ resolved = true, requiresAuthority = false, policyConflict = false, blocked = false } = {}) {
  return !resolved || requiresAuthority || policyConflict || blocked ? "UPLINK" : "CROSSTALK";
}

export function orderEnvelope({ id, from = "management", to, payload = null } = {}) {
  if (!id || !to) throw new Error("Order requires id and to");
  return { id: String(id), channel: "ORDERS", from: String(from), to: String(to), payload };
}

export function uplinkEnvelope({ id, from, to = "management", status, payload = null } = {}) {
  if (!id || !from || !status) throw new Error("Uplink requires id, from and status");
  return { id: String(id), channel: "UPLINK", from: String(from), to: String(to), status: String(status), payload };
}
