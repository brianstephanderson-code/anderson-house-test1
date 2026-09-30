// MISSING-UNIVERSE PREDICTION GATE
// Turn an explanation into a test: if it is right, what should an independent carrier universe contain?
// Record the prediction before opening that universe so the target is not rewritten after the result.

export function missingUniversePredictionGate({
  explanation='',
  sourceUniverses=[],
  targetUniverse='',
  predictedObservation='',
  predictionRecordedBeforeSearch=false,
  observed=null,
}={}) {
  let state='form-prediction';
  if (explanation && targetUniverse && predictedObservation && predictionRecordedBeforeSearch) state='prediction-ready';
  if (state==='prediction-ready' && observed===true) state='prediction-met';
  if (state==='prediction-ready' && observed===false) state='prediction-failed-recast';

  return {
    missingUniversePrediction:{
      explanation,
      sourceUniverses:[...new Set(sourceUniverses)],
      targetUniverse,
      predictedObservation,
      predictionRecordedBeforeSearch,
      observed,
      state,
      rule:'PREDICT BEFORE YOU LOOK; THEN LET THE NEW UNIVERSE ANSWER BACK'
    }
  };
}
