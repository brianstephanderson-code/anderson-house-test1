// RELATIONSHIP BRIDGE POOL GATE
// Keep multiple proven bridges available. A bridge proven in one context is not universal.
// Expose only bridges whose proven context constraints fit the current gap.

export function relationshipBridgePoolGate({qualifiedBridges=[],currentContextTags=[]}={}) {
  const current=new Set(currentContextTags);
  const available=qualifiedBridges.filter(b=>b.available!==false);
  const compatible=available.filter(b=>{
    const requires=b.contextRequires??[];
    return requires.every(tag=>current.has(tag));
  });

  return {relationshipBridgePool:{
    available:available.map(b=>b.bridgeId),
    compatible:compatible.map(b=>b.bridgeId),
    state:compatible.length?'proven-bridges-available':'recast-relationship-universes',
    universalBridge:null,
    rule:'KEEP PROVEN BRIDGES, BUT ROUTE THEM BY CONTEXT; A BRIDGE IS NOT UNIVERSAL JUST BECAUSE IT WORKED ONCE'
  }};
}
