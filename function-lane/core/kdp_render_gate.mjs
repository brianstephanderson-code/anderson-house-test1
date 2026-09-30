const KDP_SPEC_2026_09_30 = Object.freeze({
  sourceDate: '2026-09-30',
  paperback: {
    customTrimInches: { minWidth: 4, maxWidth: 8.5, minHeight: 6, maxHeight: 11.69 },
    largeTrimThresholdInches: { widthOver: 6.12, heightOver: 9 },
    bleedExtensionInches: { width: 0.125, height: 0.25 },
    outsideMarginMinInches: { noBleed: 0.25, bleed: 0.375 },
    insideMarginByPageCount: [
      { minPages: 24, maxPages: 150, inside: 0.375 },
      { minPages: 151, maxPages: 300, inside: 0.5 },
      { minPages: 301, maxPages: 500, inside: 0.625 },
      { minPages: 501, maxPages: 700, inside: 0.75 },
      { minPages: 701, maxPages: 828, inside: 0.875 },
    ],
  },
  ebook: {
    preferredInterchange: 'EPUB',
    validationTool: 'Kindle Previewer',
    reflowablePreferredForTextHeavyBooks: true,
  },
});

function requiredInsideMargin(pageCount) {
  const band = KDP_SPEC_2026_09_30.paperback.insideMarginByPageCount
    .find((x) => pageCount >= x.minPages && pageCount <= x.maxPages);
  return band?.inside ?? null;
}

function round3(n) {
  return Math.round(n * 1000) / 1000;
}

export function buildKdpRenderGate({
  styleLayout,
  format,
  paperback = {},
} = {}) {
  if (!styleLayout || styleLayout.state !== 'STYLE_LAYOUT_RULES_READY') {
    throw new Error('STYLE_LAYOUT_RULES_READY input is required');
  }
  if (styleLayout.sourceIntegrity?.sourceTextUnchanged !== true) {
    throw new Error('source integrity must be preserved');
  }

  if (format === 'ebook') {
    return {
      state: 'KDP_EBOOK_RENDER_CONTRACT_READY',
      platform: 'Amazon KDP',
      specDate: KDP_SPEC_2026_09_30.sourceDate,
      sourceIntegrity: { ...styleLayout.sourceIntegrity },
      contract: {
        interchange: KDP_SPEC_2026_09_30.ebook.preferredInterchange,
        validateWith: KDP_SPEC_2026_09_30.ebook.validationTool,
        reflowable: true,
        preserveSemanticRoles: true,
        preserveParagraphIds: true,
        readerAidLayerSeparateFromSource: true,
      },
      nextState: 'READY_FOR_EPUB_TEST_RENDER',
    };
  }

  if (format !== 'paperback') throw new Error('format must be paperback or ebook');

  const width = Number(paperback.trimWidthInches);
  const height = Number(paperback.trimHeightInches);
  const bleed = Boolean(paperback.bleed);
  const pageCount = paperback.pageCount == null ? null : Number(paperback.pageCount);
  const bounds = KDP_SPEC_2026_09_30.paperback.customTrimInches;

  if (!Number.isFinite(width) || !Number.isFinite(height)) {
    throw new Error('paperback trim width and height are required');
  }
  if (width < bounds.minWidth || width > bounds.maxWidth ||
      height < bounds.minHeight || height > bounds.maxHeight) {
    throw new Error('trim size is outside KDP paperback custom-trim bounds');
  }

  const largeTrim =
    width > KDP_SPEC_2026_09_30.paperback.largeTrimThresholdInches.widthOver ||
    height > KDP_SPEC_2026_09_30.paperback.largeTrimThresholdInches.heightOver;

  const pageSize = bleed
    ? {
        widthInches: round3(width + KDP_SPEC_2026_09_30.paperback.bleedExtensionInches.width),
        heightInches: round3(height + KDP_SPEC_2026_09_30.paperback.bleedExtensionInches.height),
      }
    : { widthInches: width, heightInches: height };

  const outsideMarginMinInches = bleed
    ? KDP_SPEC_2026_09_30.paperback.outsideMarginMinInches.bleed
    : KDP_SPEC_2026_09_30.paperback.outsideMarginMinInches.noBleed;

  if (pageCount == null) {
    return {
      state: 'KDP_PRINT_GATE_NEEDS_PAGINATION',
      platform: 'Amazon KDP',
      specDate: KDP_SPEC_2026_09_30.sourceDate,
      sourceIntegrity: { ...styleLayout.sourceIntegrity },
      provisionalContract: {
        trimSizeInches: { width, height },
        manuscriptPageSizeInches: pageSize,
        bleed,
        largeTrim,
        outsideMarginMinInches,
      },
      missing: ['final test-render pageCount', 'inside/gutter margin derived from pageCount'],
      nextState: 'RUN_TEST_PAGINATION',
    };
  }

  if (!Number.isInteger(pageCount) || pageCount < 1) throw new Error('pageCount must be a positive integer');
  const insideMarginMinInches = requiredInsideMargin(pageCount);
  if (insideMarginMinInches == null) {
    return {
      state: 'RECAST_PLATFORM_SPEC',
      platform: 'Amazon KDP',
      specDate: KDP_SPEC_2026_09_30.sourceDate,
      reason: 'page count falls outside the generic margin table encoded in this gate; verify the exact KDP print option before rendering',
      pageCount,
    };
  }

  return {
    state: 'KDP_PAPERBACK_RENDER_CONTRACT_READY',
    platform: 'Amazon KDP',
    specDate: KDP_SPEC_2026_09_30.sourceDate,
    sourceIntegrity: { ...styleLayout.sourceIntegrity },
    contract: {
      trimSizeInches: { width, height },
      manuscriptPageSizeInches: pageSize,
      bleed,
      largeTrim,
      pageCount,
      marginsMinInches: {
        inside: insideMarginMinInches,
        outside: outsideMarginMinInches,
        top: outsideMarginMinInches,
        bottom: outsideMarginMinInches,
      },
      preserveSemanticRoles: true,
      preserveParagraphIds: true,
      readerAidLayerSeparateFromSource: true,
    },
    nextState: 'READY_FOR_PRINT_TEST_RENDER_AND_PREVIEW',
  };
}

export { KDP_SPEC_2026_09_30 };
