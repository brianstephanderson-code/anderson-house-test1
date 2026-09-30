// UNIVERSE RECAST GATE
// When evidence is insufficient, decide what level actually needs changing:
// query -> meadow -> carrier universe. Do not keep casting the same net harder.

export function universeRecastGate({
  sufficient = false,
  queryFramesExhausted = false,
  currentMeadowExhausted = false,
  usefulNewEvidenceLastCast = true,
  alternateMeadows = [],
  alternateUniverses = [],
} = {}) {
  let action = 'done';
  let targets = [];

  if (!sufficient) {
    if (!queryFramesExhausted && usefulNewEvidenceLastCast) {
      action = 'change-query-frame';
    } else if (!currentMeadowExhausted && alternateMeadows.length) {
      action = 'change-meadow';
      targets = alternateMeadows;
    } else if (alternateUniverses.length) {
      action = 'change-carrier-universe';
      targets = alternateUniverses;
    } else {
      action = 'open-carrier-cast';
    }
  }

  return {
    universeRecast: {
      action,
      targets,
      sufficient,
      rule: 'WHEN THE NET STOPS LEARNING, CHANGE THE NET, THE MEADOW, OR THE UNIVERSE',
    },
  };
}
