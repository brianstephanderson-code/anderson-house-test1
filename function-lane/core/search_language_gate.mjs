// SEARCH LANGUAGE GATE
// The language and spelling of the query shape what the net can catch.
// Check relevant languages, historical spellings, transliterations and obsolete names before treating search agreement as broad coverage.

export function searchLanguageGate({
  relevantLanguages = [],
  searchedLanguages = [],
  historicalFormsExpected = [],
  searchedHistoricalForms = [],
  transliterationsExpected = [],
  searchedTransliterations = [],
  obsoleteTermsExpected = [],
  searchedObsoleteTerms = [],
} = {}) {
  const missing = (expected, searched) => {
    const have = new Set(searched);
    return expected.filter(x => !have.has(x));
  };

  const gaps = {
    languages: missing(relevantLanguages,searchedLanguages),
    historicalForms: missing(historicalFormsExpected,searchedHistoricalForms),
    transliterations: missing(transliterationsExpected,searchedTransliterations),
    obsoleteTerms: missing(obsoleteTermsExpected,searchedObsoleteTerms),
  };
  const gapCount = Object.values(gaps).reduce((n,a)=>n+a.length,0);

  return {
    searchLanguage: {
      state: gapCount ? 'recast-query-language' : 'language-coverage-characterized',
      gaps,
      gapCount,
      rule: "THE NET'S LANGUAGE CAN DECIDE WHAT THE NET CATCHES",
    },
  };
}
