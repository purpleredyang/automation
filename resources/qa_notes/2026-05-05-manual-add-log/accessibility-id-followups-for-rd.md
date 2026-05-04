# Accessibility ID Follow-ups For RD

Date: 2026-05-05
Flow: Manual Add Dive Log

## 1. Mine page log card container lacks a stable semantic Accessibility ID

Current issue:

- On the `我的` page, the newly created log card is visible and can be validated by title.
- But the card container itself does not expose a stable, semantic Accessibility ID for reliable tapping.
- Inspector selection currently surfaces `GradientView.view`, which is only a visual-layer element and not a good long-term automation locator.

Impact:

- We can verify the card by title.
- We currently open the first card by positional fallback instead of a stable card/container ID.

Recommended RD action:

- Expose a stable tappable identifier for each Mine-page log card container.
- Examples:
  - `DiveLogCollectionViewCell.cell`
  - `MineLogCardView.container`
  - `MineLogCollectionCell.cardView`

Expectation:

- The identifier should represent the semantic log card, not an internal visual layer such as `GradientView.view`.

## 2. Add-photo source action sheet options do not expose stable app-owned Accessibility IDs

Current issue:

- On the photo add action sheet, options such as `潛點` are currently surfaced as localized text.
- Appium Inspector shows the selector as the visible label itself, not a stable app-owned identifier.

Impact:

- Current automation uses localized text fallback.
- This is weaker because it depends on UI language.

Recommended RD action:

- Add stable identifiers for the source options.
- Examples:
  - `AddPhotoActionSheet.spotButton`
  - `AddPhotoActionSheet.shopButton`
  - `AddPhotoActionSheet.cancelButton`

Expectation:

- These identifiers should stay stable across languages.
- Display text can still be localized separately through label/title.
