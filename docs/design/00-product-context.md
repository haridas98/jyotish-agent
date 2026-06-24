# Product Context

## Product

Jyotish Agent is a private technical Jyotish chart workspace.

## Primary Users

- Operator/owner reviewing calculated charts.
- Future astrologer-style reviewer using chart facts, dashas, vargas, and source evidence.
- Future end user only after the technical and interpretation layers are stable.

## Core Problem

The service must make complex chart calculations understandable and inspectable before AI interpretation quality is trusted.

## Current Functional Truth

- Saved chart creation and detail routes exist.
- Saved charts can be calculated.
- `/charts/:id` and `/charts/demo-d1` expose technical calculation context.
- D1-D60 implemented workbench scopes are visible.
- Classical and dasha payload status is visible.
- `/launch-status` shows live health/deploy commit.

## Product Character

Quiet professional workspace, not a marketing site.

The visual design should feel:

- precise;
- calm;
- dense where needed;
- readable for long sessions;
- serious enough for expert review.

## Do Not Break

- Calculation payload visibility.
- Existing saved chart workflow.
- Launch diagnostics.
- Read-only production smoke assumptions.
- Witness-only JH/PL policy.
- OCR separation policy.
