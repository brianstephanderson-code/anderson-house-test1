import { interpretSearchInput } from "./search_function_interpreter.mjs";
import { createSearchBlackboard } from "./search_blackboard.mjs";

function uniq(xs=[]){
  const out=[]; const seen=new Set();
  for(const x of xs){
    const v=String(x??"").replace(/\s+/g," ").trim();
    const k=v.toLowerCase();
    if(!v||seen.has(k)) continue;
    seen.add(k); out.push(v);
  }
  return out;
}

function boundaryText(boundary){
  if(!boundary?.value || !boundary?.unit) return "";
  return `${boundary.value} ${boundary.unit}`;
}

export function compileSearchQueriesFromState(state={}, maxVariants=4){
  const raw=String(state.raw??"").trim();
  const target=String(state.target??"").trim();
  const origin=String(state.origin??"").trim();
  const times=Array.isArray(state.time)?state.time:[];
  const environment=Array.isArray(state.environment)?state.environment:[];
  const unknown=String(state.unknown??"").trim();
  const action=String(state.action??"").trim();
  const distance=boundaryText(state.boundary);

  if(!raw && !target && !origin && !unknown) {
    return {ok:false,function:"SEARCH_QUERY_COMPILER",error:"EMPTY_STATE",state,queries:[]};
  }

  const essentials=uniq([
    target,
    origin,
    ...environment,
    ...times,
    unknown
  ]).join(" ");

  const focused=uniq([
    target ? '"'+target+'"' : "",
    origin,
    ...environment,
    ...times,
    unknown
  ]).join(" ");

  const actionCast=uniq([
    target,
    action,
    origin,
    ...environment,
    unknown
  ]).join(" ");

  const booleanTerms=uniq([
    target ? '"'+target+'"' : "",
    origin,
    ...environment,
    ...times,
    unknown
  ]);
  const boolean=booleanTerms.join(" AND ");

  const boundaryCast=uniq([
    target,
    origin,
    ...environment,
    unknown,
    distance
  ]).join(" ");

  const candidates=[
    {kind:"FUNCTIONAL_ESSENTIALS",query:essentials},
    {kind:"FUNCTIONAL_FOCUSED",query:focused},
    {kind:"FUNCTIONAL_ACTION",query:actionCast},
    {kind:"FUNCTIONAL_BOOLEAN",query:boolean},
    {kind:"FUNCTIONAL_BOUNDARY",query:boundaryCast},
    {kind:"ORIGINAL_FALLBACK",query:raw}
  ].filter(x=>x.query);

  const seen=new Set(); const queries=[];
  for(const x of candidates){
    const k=x.query.toLowerCase().replace(/\s+/g," ").trim();
    if(!k||seen.has(k)) continue;
    seen.add(k); queries.push(x);
    if(queries.length>=Math.max(1,Math.min(Number(maxVariants)||4,6))) break;
  }

  return {ok:true,function:"SEARCH_QUERY_COMPILER",state,queries};
}

export function compileSearchQueries(text="", maxVariants=4){
  const interpreted=interpretSearchInput(text);
  if(!interpreted.ok) return {ok:false,function:"SEARCH_QUERY_COMPILER",error:interpreted.error,state:{raw:String(text??"")},queries:[]};
  const blackboard=createSearchBlackboard(interpreted);
  return compileSearchQueriesFromState(blackboard.state,maxVariants);
}
