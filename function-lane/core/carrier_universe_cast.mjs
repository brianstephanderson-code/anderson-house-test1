// CARRIER / MECHANISM CAST
// Before choosing search doors, ask what mechanisms could carry evidence of the unknown.
// Meadows come after universes.

export function carrierUniverseCast({purpose='',unknown='',candidateCarriers=[]}={}) {
  const carriers=[...new Set(candidateCarriers.filter(Boolean))];
  const defaultUniverses=['document','people','practice','object','place','environment','language','institution','measurement','digital'];
  const unexplored=defaultUniverses.filter(x=>!carriers.includes(x));
  return {
    carrierCast:{
      purpose,unknown,carriers,unexplored,
      state: purpose && unknown && carriers.length ? 'universes-open' : 'recast-carriers',
      rule:'SEARCH FOR POSSIBLE CARRIERS BEFORE SEARCHING FOR THE ANSWER'
    }
  };
}
