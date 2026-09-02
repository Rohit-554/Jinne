# Baseline Comparison

Report: `eval/results/comparison-20260902T054132Z.json`

Provenance: `baseline_a_context_only` and `baseline_b_naive_vector_memory` were run fresh, live, against all 50 scenarios. `proposed_system` reuses the already-measured canonical `evaluation-harness` results (`eval/results/run-20260902T044829Z.json`) rather than being re-run a third time, since it hasn't changed - see `baseline-comparison`'s design.md for why. All three runs hit Groq's free-tier daily token cap at least once during data collection; every number below comes from a scenario that actually completed against a live model, never a rate-limit failure.

## Results

| Category | Proposed System | Baseline A (context only) | Baseline B (naive vector memory) |
|---|---|---|---|
| Factual recall | 100% | 100% | 100% |
| Long-range recall | 100% | 100% | 100% |
| Contradiction/update | 100% | 90% | 90% |
| Temporal reasoning | 100% | 100% | 100% |
| Persona consistency | 90% | 90% | 90% |
| **Overall** | **98% (49/50)** | **96% (48/50)** | **96% (48/50)** |

## The honest headline: the gap is small, and here's why

Both baselines score almost as well as the proposed system on this scenario suite. That is a real result, not a disappointing one to explain away - and it points at a genuine limitation of the scenario suite itself, not evidence that the architecture doesn't matter.

Every scenario in this suite runs within a **single session**, a handful of turns, well within what a full raw conversation transcript can hold. Baseline A (no memory at all) gets the *entire* conversation as context on every turn - for something this short, "no persistent memory" and "everything is remembered because it's still on screen" are indistinguishable. Baseline B keeps a rolling window of recent raw turns on top of its naive vector memory, which covers most of the same ground. Neither baseline had to actually forget anything to be tested here.

The place structured persistent memory is *not optional* - surviving a full process restart with zero in-memory state - was proven separately and concretely in the P0 milestone demo (`companion-memory-core-loop`): a brand-new process, no chat history, correctly recalled "Bruno" purely from a SQLite row. Neither baseline can do that at all: Baseline A has no persistence mechanism, period; Baseline B's memory only outlives a process if it's pointed at a real file, which this evaluation harness deliberately doesn't do (each scenario gets an isolated `:memory:` store, matching how `evaluation-harness` already worked). This comparison measures within-session reasoning quality, not cross-session survival - and within a single short session, a strong LLM with full raw context is a genuinely competitive baseline. That's a fair, useful thing to have measured.

## Digging into the one category where a gap appears: `contra-08`

Both baselines fail the same scenario the proposed system passes - "I'm renting an apartment downtown" → "I just bought a house in the suburbs" → "Where do I live now?" (expected: *suburbs*). The two failures are not the same kind of failure:

**Baseline A's failure is real.** Its response: *"...an apartment downtown and a fresh-out-of-the-box house in the 'burbs. **Which address is your current HQ?**"* - it never commits to an answer. With both facts sitting in its raw context and no explicit "this one is current" signal, it hedged and asked the user to disambiguate instead of inferring that the more recent statement describes the present. This is exactly the failure mode structured supersede tracking exists to prevent, and it shows up even in a scenario this short.

**Baseline B's failure is a grading artifact, not a reasoning failure.** Its response: *"You've swapped the downtown hustle for a suburban pad - so you're now calling that new house in the 'burbs home."* - that is a correct answer. It says "suburban" and "'burbs," not the literal string "suburbs," so the deterministic substring check scored it FAIL. This is the same class of limitation already documented in `evaluation-harness`'s failure analysis (the Unicode-hyphen false negative) and in this change's design.md ("substring matching can false-negative on a correct-but-differently-worded answer") - accepted there as a reproducibility trade-off, and this is a fresh concrete example of it, not a new bug to chase. Fixing paraphrase-tolerant grading in general is a much larger undertaking (effectively semantic grading) than is worth doing for one observed case.

`persona-09` fails identically across all three systems, which is expected and not a meaningful comparison point: persona-consistency scenarios have no prior turns, so no system's memory architecture is even exercised there - all three build the identical persona-only prompt and hit the same model-level difficulty (an explicit "use formal corporate language" request pulling the response out of character).

## What this comparison actually supports

- The resolver's specific value (turning ambiguous multi-fact context into one confident current answer) shows up even in a small sample size, in exactly the scenario shape (two competing facts, no explicit recency marker in the question) it exists to handle.
- The bigger architectural claim - that structured, persisted memory matters - is not well-tested by same-session scenarios short enough to fit in raw context, and shouldn't be oversold from this comparison alone. The restart-survival milestone remains the stronger piece of evidence for that claim; this comparison is complementary, not a replacement for it.
