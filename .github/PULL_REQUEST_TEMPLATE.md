## Description

Briefly describe the purpose of this pull request and the changes made.

Fixes #(issue)

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement or refactoring

## Architectural Compliance (AGENTS.md Checklist)

- [ ] **Simplicity & No Useless Code**: Only required changes were made; no speculative or dead code introduced.
- [ ] **No Hallucinated APIs**: All external APIs, model IDs, and SDK methods have been verified.
- [ ] **No Fabricated Functionality**: All features are genuinely executable end-to-end (no mock demo returns).
- [ ] **Strict Typing**:
  - Frontend: Strict TypeScript adhered to (no `any`, no `@ts-ignore`).
  - Backend: Pydantic schemas and Python type hints used throughout.
- [ ] **Storybook**: Any new or modified reusable UI components include interactive stories covering all visual states.
- [ ] **Security & Secret Hygiene**: No API keys, tokens, or credentials are hardcoded or exposed to frontend/logs.

## Verification & Testing

Please describe the tests that you ran to verify your changes:

- [ ] Unit tests pass: `docker exec repomind-backend pytest tests -v`
- [ ] Live Docker integration passes: `python backend/tests/test_live_docker.py`
- [ ] Frontend builds cleanly: `npm run build` (if frontend modified)
- [ ] Storybook builds: `npm run build-storybook` (if UI modified)
- [ ] Documentation audit passes: `python scripts/audit_docs.py` (if docs modified)

## Screenshots / Artifacts (if applicable)

Attach screenshots, Storybook previews, or TraceNest telemetry event samples.
