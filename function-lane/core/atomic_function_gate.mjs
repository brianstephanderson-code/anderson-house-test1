// ATOMIC FUNCTION GATE
// Find the smallest useful independently testable job.
// Smaller is useful only while splitting preserves context and reduces total work.

export function atomicFunctionGate({
  job='',
  independentlyTestable=false,
  usefulOutput=false,
  canSplitFurther=false,
  splitPreservesContext=true,
  splitReducesTotalCost=true,
  handoffCostHigh=false,
}={}) {
  let state='recast-job';

  if (!independentlyTestable || !usefulOutput) state='recast-job';
  else if (canSplitFurther && splitPreservesContext && splitReducesTotalCost && !handoffCostHigh) state='shred-further';
  else state='atomic-ready';

  return {
    atomicFunction:{
      job,state,
      independentlyTestable,usefulOutput,canSplitFurther,
      splitPreservesContext,splitReducesTotalCost,handoffCostHigh,
      rule:'USE THE SMALLEST USEFUL INDEPENDENT FUNCTION, NOT THE SMALLEST POSSIBLE PIECE'
    }
  };
}
