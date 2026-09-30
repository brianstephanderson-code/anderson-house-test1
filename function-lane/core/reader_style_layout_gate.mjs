const DEFAULT_STYLE_PROFILE = Object.freeze({
  profileId: 'READER_EDITION_BASE_001',
  principles: [
    'Preserve source wording and paragraph order.',
    'Reader aids are visually distinct from Irving text.',
    'Reader aids remain subordinate to the reading experience.',
    'Do not encode vendor-specific print dimensions in the literary style layer.',
    'Keep semantic roles separate so downstream print and ebook renderers can adapt them independently.',
  ],
  roles: {
    title: { kind: 'display', emphasis: 'strong', breakBefore: true },
    author: { kind: 'display', emphasis: 'medium', breakBefore: false },
    frame: { kind: 'body', emphasis: 'normal', breakBefore: false },
    epigraph: { kind: 'quotation', emphasis: 'medium', breakBefore: false },
    body: { kind: 'body', emphasis: 'normal', breakBefore: false },
    readerAid: { kind: 'support', emphasis: 'subordinate', breakBefore: false },
  },
  readerAidPolicy: {
    admissionState: 'VERIFIED_READER_AID',
    permittedPlacements: ['margin-equivalent', 'footnote-equivalent', 'endnote-equivalent', 'tap-note-equivalent'],
    mayReplaceSourceText: false,
    mayInterruptSourceParagraph: false,
    mustCarryJobId: true,
    mustCarryParagraphId: true,
  },
});

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function buildReaderStyleLayoutProfile({ shell, overrides = {} } = {}) {
  if (!shell || shell.state !== 'SHELL_READY') throw new Error('SHELL_READY reader edition shell is required');
  if (shell.sourceIntegrity?.sourceTextUnchanged !== true) throw new Error('source integrity must be preserved');

  const profile = clone(DEFAULT_STYLE_PROFILE);
  if (overrides.roles) {
    for (const [role, patch] of Object.entries(overrides.roles)) {
      if (!profile.roles[role]) throw new Error(`unknown semantic role: ${role}`);
      profile.roles[role] = { ...profile.roles[role], ...patch };
    }
  }

  for (const slot of shell.supportSlots ?? []) {
    if (slot.readerFacingEligible && slot.state !== profile.readerAidPolicy.admissionState) {
      throw new Error(`reader-facing slot ${slot.jobId} is not verified`);
    }
  }

  return {
    state: 'STYLE_LAYOUT_RULES_READY',
    profile,
    sourceIntegrity: {
      sha256: shell.sourceIntegrity.sha256,
      sourceTextUnchanged: true,
    },
    renderContract: {
      paragraphIdsPreserved: true,
      semanticRolesRemainSeparate: true,
      vendorSpecificSizingDeferred: true,
      readerAidLayerSeparateFromSource: true,
    },
  };
}
