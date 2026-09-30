import { checkDistanceBoundary } from "./search_boundary.mjs";

function norm(v=""){ return String(v??"").toLowerCase().replace(/[^a-z0-9]+/g," ").replace(/\s+/g," ").trim(); }

export function verifyEvidenceBoundary(evidence={},state={}){
  const boundary=state.boundary??null;
  if(!boundary) return {
    required:false,
    verified:true,
    pass:true,
    reason:"NO_DISTANCE_BOUNDARY"
  };

  const origin=String(state.origin??"").trim();
  const originLocation=state.origin_location??null;
  if(!origin || !originLocation) return {
    required:true,
    verified:false,
    pass:false,
    reason:"ORIGIN_NOT_RESOLVED"
  };

  const title=norm(evidence.title);
  const originNorm=norm(origin);
  const titleAnchored=originNorm && title.split(" ").includes(originNorm);

  if(!titleAnchored) return {
    required:true,
    verified:false,
    pass:false,
    reason:"EVIDENCE_PLACE_NOT_YET_ANCHORED"
  };

  const distance=checkDistanceBoundary(originLocation,originLocation,boundary);
  return {
    required:true,
    verified:!!distance.ok,
    pass:!!distance.pass,
    reason:distance.pass?"TITLE_ANCHORED_TO_ORIGIN":"OUTSIDE_BOUNDARY",
    anchor:{
      name:originLocation.name??origin,
      lat:originLocation.lat,
      lon:originLocation.lon,
      provider:originLocation.provider??null
    },
    distance
  };
}

export function applyBoundaryEvidence(evidence=[],state={}){
  return (Array.isArray(evidence)?evidence:[]).map(x=>({
    ...x,
    boundary_verification:verifyEvidenceBoundary(x,state)
  }));
}
