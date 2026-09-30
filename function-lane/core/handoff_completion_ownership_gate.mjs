// HANDOFF COMPLETION OWNERSHIP GATE
// A mid-job handoff must leave exactly one active owner for every unfinished work unit.
// Prevent orphaned work and double ownership after replacement.

export function handoffCompletionOwnershipGate({remainingWork=[],assignments=[]}={}) {
  const active=assignments.filter(a=>a?.active===true);
  const ownersFor=step=>active.filter(a=>(a.work??[]).includes(step)).map(a=>a.functionId).filter(Boolean);
  const ownership=remainingWork.map(step=>({step,owners:ownersFor(step)}));
  const orphaned=ownership.filter(x=>x.owners.length===0).map(x=>x.step);
  const duplicated=ownership.filter(x=>x.owners.length>1).map(x=>x.step);
  const clean=!orphaned.length&&!duplicated.length;
  return {handoffCompletionOwnership:{
    ownership,orphaned,duplicated,
    state:clean?'ownership-closed':'ownership-gap',
    action:clean?'release-remaining-work':'reconcile-work-ownership',
    rule:'EVERY UNFINISHED UNIT MUST HAVE ONE ACTIVE OWNER; ZERO OWNERS LOSES WORK, TWO OWNERS DUPLICATE IT'
  }};
}
