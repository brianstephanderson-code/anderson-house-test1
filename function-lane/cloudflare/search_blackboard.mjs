function uniq(xs=[]){
  const out=[]; const seen=new Set();
  for(const x of xs){ const v=String(x??"").trim(); const k=v.toLowerCase(); if(!v||seen.has(k)) continue; seen.add(k); out.push(v); }
  return out;
}

export function createSearchBlackboard(interpreted={}){
  if(!interpreted?.ok) return {ok:false,function:"SEARCH_BLACKBOARD",error:"BAD_INTERPRETER_STATE"};
  const roles=interpreted.roles||{};
  return {
    ok:true,
    function:"SEARCH_BLACKBOARD",
    state:{
      raw:interpreted.raw??"",
      purpose:"search",
      action:roles.action??null,
      target:roles.target??null,
      time:uniq(roles.time||[]),
      origin:roles.origin??null,
      boundary:roles.boundary??null,
      environment:uniq(roles.environment||[]),
      what:roles.what??null,
      desired_done:roles.desired_done??"verified answer"
    },
    casts:[],
    evidence:[],
    missing:[],
    sufficient:false,
    history:[
      {event:"INTERPRETED",by:interpreted.function??"SEARCH_FUNCTION_INTERPRETER"}
    ]
  };
}

export function appendBlackboardHistory(blackboard={},event={}){
  return {
    ...blackboard,
    history:[...(Array.isArray(blackboard.history)?blackboard.history:[]),event]
  };
}
