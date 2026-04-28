# automation

Automatic test workspace for `diverout-automation`.

## Codex Setup

This repository now includes shared Codex instructions in [AGENTS.md](AGENTS.md) and project-local skills under `.agents/skills/`.

## Recommended Skills

- `ios-simulator-skill`: Best fit for day-to-day iOS app launch, navigation, simulator lifecycle, accessibility checks, and debugging.
- `test-case-generator-skill`: Best fit when turning product requirements or QA notes into structured test cases for Sheets or test planning.
- `e2e-studio-tests`: Use when the task is specifically about running or debugging Studio Playwright end-to-end tests.
- `interior-design-expert`: Migrated from the previous workspace and available here, but not directly related to this repo's main automation workflow.

## Local Environment

Create a local `.env` from [.env.example](./.env.example) for secrets and machine-specific settings.

Example values:

```env
SESSION_ID=your-session-id
CDN_COOKIE=optional-cdn-cookie
AUTH_ID=optional-auth-id
BUNDLE_ID=com.diverout.diverout.dev
APPIUM_SERVER_URL=http://127.0.0.1:4723
```

The repository ignores `.env`, so your local secrets stay out of git history.

## Migrated Documentation

- `resources/AccessibilityIdentifiers/`
- `resources/Repository/Repository/IAP/SubscriptionEventsTracking.md`
- `resources/Repository/Repository/Sync/SYNC_FLOW.md`
- `scripts_review.md`
