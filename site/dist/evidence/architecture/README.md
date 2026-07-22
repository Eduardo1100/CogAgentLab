# Continuity of Mind architecture provenance

This directory records two related but non-identical architecture boundaries for
the project showcase. `manifest.json` describes the owner-supplied presentation deck
`Cognitive LLM Agents-slides(2).pptx`, presented by Eduardo Cortes at the
Berkeley Agent Summit in summer 2025. The editable PPTX is not bundled; all 17
slides are preserved as 1600×900 PNG renderings in `rendered_slides/` and shown
in the public showcase. A text-only editorial adaptation is preserved in
`reframed_slides/`; it changes editable prose but leaves every architecture
diagram, chart, embedded image, connector, and other visual object unchanged.
The original renderings remain bundled as the historical source. The public
`site/theory.html` essay explains the runtime in operational language;
`theory.json` preserves that interpretation in machine-readable form, and
`run_architecture.json` separately reconstructs the
runtime behind the March 2025 evaluation from the same-day code and preserved
chat traces.

The deck's title slide names Eduardo Cortes, Aaron Zheng, Yixiao Wang, Bhaskar
Mishra, Bingyi Chen, and Will Cai. Per Eduardo's account, the six-name line
preserved the original hackathon-team credit because the hackathon win supplied
the summit presentation opportunity. It is not a contribution map for the later
evaluated implementation.

## What the deck supports

- Slides 3–5 frame the context window as a cognitive global workspace managed
  by a context-sensitive meta-agent controller.
- Slides 6 and 10 describe specialized cognition loops spanning perception,
  executive control, belief, imagination, motor output, memory, and learning.
- Slides 7–12 distinguish conceptual and episodic memory flows.
- Slide 14 states that the 139-task evaluation used enhanced planning and
  active conceptual memory while excluding episodic memory. The run-specific
  audit makes that shorthand precise: retrieval of earlier episode transcripts
  was excluded, while a time-ordered observation trace for the current game was
  active.
- Slide 15 reports smaller component experiments; those values are not promoted
  as the main showcase result.
- Slide 16 presents a future unified-substrate direction, not an implemented or
  evaluated feature of the 139-game system.

The canonical success count and dataset interpretation continue to come from
the W&B exports in `evidence/alfworld_20250328/`, not from the presentation.
The slide renderings preserve the presentation as delivered; their inclusion
does not promote every experimental result into a canonical project claim.

## How to read the historical terminology

The evaluated source called one routed role `Conscious_Agent` and labeled its
text output `World Model:`. Operationally, the role ran after environment
feedback and produced a revisable account of task state, progress, and
uncertainty; it did not choose actions. The showcase therefore describes it as
a **belief-state updater** and its output as a **belief state** while retaining
the exact historical names in provenance records. Neither label implies
sentience, phenomenal consciousness, or a learned environment simulator.

The “global workspace” is likewise used as an engineering description: a
bounded shared context plus a constrained speaker-transition policy. The focus
branch replayed the task and latest percept to re-ground that context. The
memory branches restored a current-game observation trace and representative
cross-game rules. The public theory page develops this interpretation for
readers, while `theory.json` records its aliases, sources, and boundaries.

The owner-supplied unpublished paper draft by Yixiao Wang and Aaron Zheng is an
interpretive source for this explanation. It is not bundled and is not used to
establish the canonical success count, dataset split, or exact run
configuration.

## What the run-specific audit supports

- Twelve named roles were active in a constrained AutoGen speaker-transition
  graph. A thirteenth memory-summarizer role appeared in source but was not
  routed into the group chat.
- The main cycle was `Conscious → Planning → Motor → External Perception →
  Conscious`, with explicit focus, retrieval, imagination, and learning
  branches.
- `retrieve_memory()` returned both the current game's observation history and
  representative cross-game conceptual rules.
- New rules were appended to `memory1.txt`, embedded with MiniLM, clustered with
  KMeans, and reduced to representative rules in `memory2.txt` between games.
- The 60-action budget was exposed as two 30-action phases, with reflection and
  learning available before a recovery phase.

The trace audit covers 139 game directories. Game 123 contains only the
preserved no-chat-history error; the other 138 chat files expose the role and
transition evidence summarized in `run_architecture.json`.

## Chronology boundary

Eduardo describes the hackathon phase as collaborative component research that
he integrated into a Global Workspace Theory architecture. He designed that
architecture and made a substantial contribution to the team presentation; the
presentation covered intended design principles and component results rather
than the later 139-game evaluation.

After the hackathon, Eduardo became the team's main organizer and took on an
informal leadership role, but he was never formally designated team leader.
Yixiao Wang occasionally advised him. Eduardo reports that he then implemented
and evaluated the integrated architecture independently within a different but
overlapping GenAI at Berkeley project sponsored by Block, Inc. This contribution
and sponsorship chronology is owner-attested; it is not established by the
summit deck itself.

CogAgentLab is the later post-graduation extension that adds multi-environment
evaluation, instrumentation, and a coding-agent improvement loop.

The hackathon certificate is owner-held but is not included in this public
evidence bundle.
