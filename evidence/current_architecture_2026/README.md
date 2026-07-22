# Current CogAgentLab architecture snapshot

This directory records a source-audited snapshot of the CogAgentLab runtime as
of 2026-07-21. The immutable runtime source boundary is commit
`dce757481805583c91ddb1502a2c6ffc26482d47`; later showcase-only commits did not
modify the audited modules.

## What is implemented

- A shared adapter protocol covers ALFWorld, ScienceWorld, Tales, and NetHack.
- Twelve active AutoGen roles coordinate through a constrained transition graph
  and custom speaker-selection policy.
- A typed `DecisionState` separates action surface, goal, grounding, option,
  progress, and uncertainty state.
- Low-risk action sequences can run on a guarded fast path. State changes,
  failures, referent ambiguity, interrupted options, and periodic checks route
  the system through belief revision and higher-cost deliberation.
- Current-game summaries, retrieved prior episodes, and clustered conceptual
  knowledge form distinct memory channels. Writes are disabled on ALFWorld
  `valid_unseen` evaluation.
- Experiment metadata, transcripts, analyst traces, architecture metrics, W&B
  data, and object-store artifacts feed an iteration driver that can hand a
  bounded change prompt to Claude Code or Codex for human review.

## Boundary

This is a structural source audit, not a claim that the current architecture has
matched the historical 87.05% result in every environment. The repository's own
architecture roadmap identifies prompt size, heuristic accumulation, and
environment coupling as active limitations. Its learned policy layer remains a
target rather than an implemented component.
