// TRANSLATION INTEGRITY GATE
// A translation is an interpretation layer, not transparent access to the source.
// Preserve the original-language state and expose choices that affect the claim.

export function translationIntegrityGate({
  sourceId = '',
  originalLanguageAvailable = false,
  originalTextRef = '',
  translatorIdentified = false,
  translationDateKnown = false,
  alternativeTranslationsChecked = false,
  interpretiveChoiceAffectsClaim = false,
  originalSenseVerified = false,
} = {}) {
  let state = 'recast-original-language';

  if (!originalLanguageAvailable) state = 'translation-only-limited';
  else if (interpretiveChoiceAffectsClaim && !originalSenseVerified) state = 'translation-contamination-risk';
  else if (originalTextRef && translatorIdentified && originalSenseVerified) state = 'translation-bridged';

  return {
    translationIntegrity: {
      sourceId,
      state,
      originalTextRef,
      translatorIdentified,
      translationDateKnown,
      alternativeTranslationsChecked,
      interpretiveChoiceAffectsClaim,
      rule: 'A TRANSLATION IS EVIDENCE PLUS AN INTERPRETATION LAYER',
    },
  };
}
