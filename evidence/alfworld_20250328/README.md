# Historical ALFWorld evidence

This directory preserves the source exports and deterministic derived records for
the historical CognitiveLLM W&B run `vee8kzls` (`golden-pyramid-593`). The run is
authentication-required on W&B, so the committed exports provide a reviewable
public evidence path without changing the original run's visibility.

## Verified result

- Dataset configured by the historical runner: ALFWorld `valid_seen`
- Loader messages for a missing solvable key: 1
- Games evaluated: 139
- Successes: 121
- Failures: 18
- Success rate: 87.05%

The result must not be described as `valid_unseen` or out-of-distribution. The
historical runner passed `train_eval="eval_out_of_distribution"` to the ALFWorld
constructor, but its configured data path was `json_2.1.1/valid_seen`.

## Contents

- `source/`: byte-preserved W&B chart exports supplied by the run owner
- `manifest.json`: source hashes, provenance URLs, interpretation constraints,
  and expected totals
- `SHA256SUMS`: generated source checksum inventory
- `derived/game_results.csv`: generated canonical 139-row result table
- `derived/summary.json`: generated aggregate summary

Regenerate or verify with:

```bash
make historical-evidence
make historical-evidence-check
```

## Known conditions

Game 123 exceeded GPT-4o's context window and is counted as a failure. W&B
records game 139 as a 60-action failure, but the local trace lacks its terminal
`result.txt`: the historical runner checked whether the final game was complete
before writing local result files. The W&B row and full action trace preserve the
outcome.

The historical code was collaborative. Git history attributes the core
`gwt_agent.py` work to Eduardo Cortes, Bhaskar Mishra, and Yixiao Wang, with
additional repository contributions from Will Cai and Aaron Zheng. The source
repository does not declare a license, so this bundle links to its raw traces
rather than copying them.
