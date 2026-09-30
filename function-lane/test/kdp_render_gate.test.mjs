import test from 'node:test';
import assert from 'node:assert/strict';
import { buildKdpRenderGate } from '../core/kdp_render_gate.mjs';

const styleLayout = {
  state: 'STYLE_LAYOUT_RULES_READY',
  sourceIntegrity: { sha256: 'abc123', sourceTextUnchanged: true },
};

test('builds a KDP ebook contract without changing source semantics', () => {
  const result = buildKdpRenderGate({ styleLayout, format: 'ebook' });
  assert.equal(result.state, 'KDP_EBOOK_RENDER_CONTRACT_READY');
  assert.equal(result.contract.interchange, 'EPUB');
  assert.equal(result.contract.validateWith, 'Kindle Previewer');
  assert.equal(result.contract.preserveParagraphIds, true);
});

test('paperback gate waits for page count before fixing the gutter', () => {
  const result = buildKdpRenderGate({
    styleLayout,
    format: 'paperback',
    paperback: { trimWidthInches: 6, trimHeightInches: 9, bleed: false },
  });
  assert.equal(result.state, 'KDP_PRINT_GATE_NEEDS_PAGINATION');
  assert.equal(result.provisionalContract.outsideMarginMinInches, 0.25);
  assert.deepEqual(result.missing, ['final test-render pageCount', 'inside/gutter margin derived from pageCount']);
});

test('derives current KDP no-bleed margin contract for a short 6x9 book', () => {
  const result = buildKdpRenderGate({
    styleLayout,
    format: 'paperback',
    paperback: { trimWidthInches: 6, trimHeightInches: 9, bleed: false, pageCount: 120 },
  });
  assert.equal(result.state, 'KDP_PAPERBACK_RENDER_CONTRACT_READY');
  assert.equal(result.contract.marginsMinInches.inside, 0.375);
  assert.equal(result.contract.marginsMinInches.outside, 0.25);
  assert.deepEqual(result.contract.manuscriptPageSizeInches, { widthInches: 6, heightInches: 9 });
});

test('adds KDP bleed dimensions to manuscript page size', () => {
  const result = buildKdpRenderGate({
    styleLayout,
    format: 'paperback',
    paperback: { trimWidthInches: 6, trimHeightInches: 9, bleed: true, pageCount: 120 },
  });
  assert.deepEqual(result.contract.manuscriptPageSizeInches, { widthInches: 6.125, heightInches: 9.25 });
  assert.equal(result.contract.marginsMinInches.outside, 0.375);
});

test('uses the larger inside margin when page count grows', () => {
  const result = buildKdpRenderGate({
    styleLayout,
    format: 'paperback',
    paperback: { trimWidthInches: 6, trimHeightInches: 9, bleed: false, pageCount: 220 },
  });
  assert.equal(result.contract.marginsMinInches.inside, 0.5);
});

test('rejects a paperback trim size outside current custom-trim bounds', () => {
  assert.throws(
    () => buildKdpRenderGate({
      styleLayout,
      format: 'paperback',
      paperback: { trimWidthInches: 3.5, trimHeightInches: 9, bleed: false, pageCount: 100 },
    }),
    /outside KDP paperback custom-trim bounds/,
  );
});
