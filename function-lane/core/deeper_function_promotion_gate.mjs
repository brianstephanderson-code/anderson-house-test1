// DEEPER FUNCTION PROMOTION GATE
// A function proven across multiple surface holes becomes a reusable parent capability.
// Keep its proof boundary, covered signatures, requirements and provenance attached.

export function deeperFunctionPromotionGate({trialResult={},provenance=[]}={}) {
  const promotable=trialResult.state==='deeper-function-proven' && !!trialResult.candidateFunction;
  return {deeperFunctionPromotion:{
    promoted:promotable?{
      functionId:trialResult.candidateFunction,
      satisfies:[...(trialResult.requirements??[])],
      proof:{
        distinctClosedSignatures:trialResult.distinctClosedSignatures??0,
        cleanTrials:trialResult.cleanTrials??0
      },
      provenance:[...provenance],
      scope:'only-within-proven-requirements-and-signature-family'
    }:null,
    state:promotable?'parent-capability-ready':'not-promotable',
    rule:'PROMOTE A REPEATEDLY PROVEN DEEPER FUNCTION, BUT KEEP ITS PROOF BOUNDARY ATTACHED'
  }};
}
