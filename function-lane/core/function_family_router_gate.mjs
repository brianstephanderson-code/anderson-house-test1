// FUNCTION FAMILY ROUTER GATE
// Route work across a healthy parent and its proven specialist children.
// Prefer the narrowest proven fit; keep multiple equal fits available for trial/load routing.

export function functionFamilyRouterGate({hole={},parent={},children=[]}={}) {
  const needs=hole.requirements??[];
  const fits=c=>c?.available!==false && (c.satisfies??[]).every(r=>needs.includes(r)) && (!(c.signatures??[]).length || c.signatures.includes(hole.signature));
  const childFits=children.filter(c=>c.proven===true && fits(c));
  const parentFits=parent?.proven===true && fits(parent);
  const routes=childFits.length?childFits.map(c=>({functionId:c.functionId,role:'specialist-child'})):(parentFits?[{functionId:parent.functionId,role:'parent'}]:[]);
  return {functionFamilyRouter:{
    holeId:hole.id??null,routes,
    state:routes.length?'family-routes-ready':'return-hole-to-discovery',
    selection:routes.length===1?routes[0].functionId:null,
    rule:'ROUTE TO THE NARROWEST PROVEN FUNCTION THAT FITS; KEEP THE PARENT FOR THE TERRITORY IT STILL OWNS'
  }};
}
