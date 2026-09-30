// FUNCTION DRIFT GATE
// A function can still 'work' while its behavior slowly changes.
// Compare recent healthy-looking runs with the proven baseline and trigger requalification when drift exceeds tolerance.

export function functionDriftGate({functionId='',baseline={},recentRuns=[],tolerance={elapsedRatio:2,errorRateDelta:0.1}}={}) {
  const completed=recentRuns.filter(r=>r?.completed===true);
  const avgElapsed=completed.length ? completed.reduce((s,r)=>s+(r.elapsed??0),0)/completed.length : null;
  const errorRate=completed.length ? completed.filter(r=>(r.errors??[]).length>0).length/completed.length : null;

  const elapsedRatio=(avgElapsed!==null && baseline.avgElapsed>0) ? avgElapsed/baseline.avgElapsed : null;
  const errorRateDelta=(errorRate!==null && baseline.errorRate!==undefined) ? errorRate-baseline.errorRate : null;
  const drift=[];
  if (elapsedRatio!==null && elapsedRatio>tolerance.elapsedRatio) drift.push('elapsed');
  if (errorRateDelta!==null && errorRateDelta>tolerance.errorRateDelta) drift.push('errors');

  return {
    functionDrift:{
      functionId,measuredRuns:completed.length,elapsedRatio,errorRateDelta,drift,
      state:drift.length?'drift-detected':'baseline-compatible',
      action:drift.length?'send-to-requalification':'keep-active',
      rule:'WATCH FOR CHANGE, NOT JUST FAILURE; A FUNCTION MAY DRIFT BEFORE IT BREAKS'
    }
  };
}
