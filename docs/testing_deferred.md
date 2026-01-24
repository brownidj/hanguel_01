# Deferred and Intentionally Ignored Tests

This document records all tests that are **intentionally skipped or ignored** in the Hangul_01 test suite.

These tests are **not broken**, **not missing**, and **not accidental skips**.  
They are deferred because the production architecture deliberately hides or abstracts the behaviour they would otherwise assert.

Each deferred test includes:
- The reason it is deferred
- The explicit condition under which it should be re-enabled
- The architectural boundary that must change
- Acceptance criteria for completion

No test should be skipped without being listed here.

---

## 1. Glyph Exposure Tests (HANGUL_TEST_MODE)

**Affected tests**
- `test_render_variants.py`
- Tests asserting glyph widgets inside segment frames

**Current behaviour**
- Production rendering uses custom paint / non-QWidget glyphs
- Glyph widgets are not discoverable via `findChild()` in normal mode
- Tests require stable, discoverable `QLabel` instances

**Why tests are deferred**
- Forcing discoverable widgets in production would weaken rendering encapsulation
- Test-only exposure is deliberately gated

**Explicit enable condition**
- Environment variable:
  ```bash
  HANGUL_TEST_MODE=1