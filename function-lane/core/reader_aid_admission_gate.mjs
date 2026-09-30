// READER AID ADMISSION GATE
// Converts verified research returns into safe assembly instructions.
// It never edits source text and never upgrades an uncertain return.

function normalizeOutcome(value) {
  return String(value ?? '').toUpperCase();
}

export function readerAidAdmissionGate({
  researchReturn = {},
  attachmentSlot = {},
} = {}) {
  const jobId = String(researchReturn.job_id ?? researchReturn.jobId ?? '');
  const slotJobId = String(attachmentSlot.job_id ?? attachmentSlot.jobId ?? '');
  const paragraphId = String(attachmentSlot.paragraph_id ?? attachmentSlot.paragraphId ?? '');
  const outcome = normalizeOutcome(researchReturn.outcome ?? researchReturn.state);

  if (!jobId) throw new Error('research return job_id is required');
  if (!slotJobId || !paragraphId) throw new Error('attachment slot job_id and paragraph_id are required');
  if (jobId !== slotJobId) throw new Error('research return does not match attachment slot');

  if (outcome === 'NO_MATERIAL_AID') {
    return {
      readerAidAdmission: {
        jobId,
        paragraphId,
        outcome,
        admitted: false,
        state: 'CLOSED_NO_INSERT',
        reason: 'Verified research found no material reader aid is warranted.',
      },
    };
  }

  if (outcome === 'RECAST') {
    return {
      readerAidAdmission: {
        jobId,
        paragraphId,
        outcome,
        admitted: false,
        state: 'RETURN_TO_RESEARCH',
        reason: String(researchReturn.missing_evidence ?? researchReturn.missingEvidence ?? 'missing evidence not specified'),
      },
    };
  }

  if (outcome !== 'VERIFIED_READER_AID') {
    return {
      readerAidAdmission: {
        jobId,
        paragraphId,
        outcome: outcome || 'UNKNOWN',
        admitted: false,
        state: 'HOLD',
        reason: 'Only explicit VERIFIED_READER_AID, NO_MATERIAL_AID, or RECAST outcomes are accepted.',
      },
    };
  }

  const passport = researchReturn.verification_passport ?? researchReturn.verificationPassport ?? {};
  if (String(passport.state ?? '').toLowerCase() !== 'verified') {
    return {
      readerAidAdmission: {
        jobId,
        paragraphId,
        outcome,
        admitted: false,
        state: 'HOLD_VERIFICATION',
        reason: 'VERIFIED_READER_AID requires a verified verification passport.',
      },
    };
  }

  const readerText = String(researchReturn.reader_aid_text ?? researchReturn.readerAidText ?? '').trim();
  if (!readerText) {
    return {
      readerAidAdmission: {
        jobId,
        paragraphId,
        outcome,
        admitted: false,
        state: 'HOLD_MISSING_TEXT',
        reason: 'Verified aid has no reader-facing text.',
      },
    };
  }

  return {
    readerAidAdmission: {
      jobId,
      paragraphId,
      outcome,
      admitted: true,
      state: 'READY_FOR_ASSEMBLY',
      readerAid: {
        term: String(researchReturn.term ?? ''),
        text: readerText,
        sourceIds: Array.isArray(passport.sources)
          ? passport.sources.map((s) => s.id).filter(Boolean)
          : [],
      },
      sourceMutationAllowed: false,
      rule: 'ADMIT VERIFIED SUPPORT; NEVER REWRITE THE MASTER TEXT',
    },
  };
}

export function planReaderAidAssembly({
  researchReturns = [],
  attachmentSlots = [],
} = {}) {
  const slotMap = new Map(
    attachmentSlots.map((slot) => [String(slot.job_id ?? slot.jobId ?? ''), slot]),
  );
  const seen = new Set();
  const admissions = [];

  for (const researchReturn of researchReturns) {
    const jobId = String(researchReturn.job_id ?? researchReturn.jobId ?? '');
    if (!jobId) throw new Error('research return job_id is required');
    if (seen.has(jobId)) throw new Error(`duplicate research return: ${jobId}`);
    seen.add(jobId);

    const slot = slotMap.get(jobId);
    if (!slot) throw new Error(`no assembly slot for ${jobId}`);
    admissions.push(readerAidAdmissionGate({ researchReturn, attachmentSlot: slot }).readerAidAdmission);
  }

  const ready = admissions.filter((x) => x.state === 'READY_FOR_ASSEMBLY');
  return {
    readerAidAssemblyPlan: {
      state: 'ASSEMBLY_PLAN_READY',
      admissions,
      counts: {
        returns: admissions.length,
        readyForAssembly: ready.length,
        closedNoInsert: admissions.filter((x) => x.state === 'CLOSED_NO_INSERT').length,
        recast: admissions.filter((x) => x.state === 'RETURN_TO_RESEARCH').length,
        held: admissions.filter((x) => x.state.startsWith('HOLD')).length,
      },
      sourceTextMutationAllowed: false,
    },
  };
}
