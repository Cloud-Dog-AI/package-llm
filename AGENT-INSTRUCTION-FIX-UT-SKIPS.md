# Agent Instruction — Fix platform-llm UT Skips

**Package:** `platform-llm`
**Date:** 2026-02-20
**Status:** OPEN — HIGH
**Problem:** 7 UT tests silently skipped out of 86 total.

---

## INTEGRITY WARRANTY

All rules from `cloud-dog-ai-platform-standards/RULES.md` apply. Read Sections 1, 2, 5 before any work.
**"ASK. DON'T GUESS. DON'T LIE. DON'T FUDGE."**

---

## PROBLEM

```
.venv/bin/pytest tests/ --env tests/env-UT --tb=no -q
→ 79 passed, 7 skipped in 0.70s
```

7 tests are skipping. Per RULES.md § 5.3.10-11:
- `pytest.skip()` is forbidden in IT/AT/QT
- Skip counts MUST be reported and justified
- UT tests should NOT skip — they don't depend on external services

---

## FIX

### Step 1 — Identify which tests skip and why

```bash
cd /opt/iac/Development/cloud-dog-ai/cloud-dog-ai-platform-standards/packages/backend/platform-llm
.venv/bin/pytest tests/ --env tests/env-UT -v --tb=short 2>&1 | grep -i "skip"
```

### Step 2 — For each skipped test, determine the cause

- **Missing optional dependency?** → Install it or mark the test correctly
- **Conditional skip on platform/Python version?** → Document and accept if legitimate
- **Skip due to missing backend/service?** → If UT, it should NOT require a backend. Fix the test or reclassify it.
- **`pytest.skip()` in fixture?** → Replace with `pytest.fail()` if the test should be mandatory

### Step 3 — Fix each skip

Either:
- Fix the condition causing the skip (preferred)
- Reclassify the test to the correct tier (if it genuinely needs an external service)
- Document the skip with explicit justification (only if unavoidable, e.g. platform-specific)

### Step 4 — Verify

```bash
.venv/bin/pytest tests/ --env tests/env-UT -v --tb=short 2>&1 | tail -5
```

**Target:** 86 passed, 0 skipped. If any skips remain, each MUST have documented justification.

---

## COMPLETION GATE

1. Every skipped test investigated and either fixed or justified
2. `pytest` output shows pass/fail/skip counts
3. Any remaining skips have explicit written justification
4. No silent skips — every skip reason visible in test output
