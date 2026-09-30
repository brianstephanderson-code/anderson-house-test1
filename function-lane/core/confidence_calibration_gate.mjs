// CONFIDENCE CALIBRATION GATE
// Confidence must describe the evidence, not our enthusiasm.
// Strong conclusion language is permitted only when the evidence passport earns it.

export function confidenceCalibrationGate({
  independentRoads = 0,
  contradictionSearch = false,
  unresolvedContradictions = 0,
  contextFit = 'pending',
  provenanceTraceable = false,
  uncertainty = null,
} = {}) {
  let level = 'unresolved';
  if (provenanceTraceable && contextFit === 'yes' && contradictionSearch) {
    if (unresolvedContradictions > 0) level = 'contested';
    else if (independentRoads >= 2) level = 'strong';
    else if (independentRoads === 1) level = 'supported';
  }
  return {
    calibration: {
      level,
      independentRoads,
      contradictionSearch,
      unresolvedContradictions,
      contextFit,
      provenanceTraceable,
      uncertainty,
      rule: 'CONFIDENCE DESCRIBES THE EVIDENCE, NOT OUR ENTHUSIASM',
    },
  };
}
