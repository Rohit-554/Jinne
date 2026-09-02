## Context

Every fact needed for the README already exists in committed files: `PLANNING.md` (requirements), `CLAUDE.md` (stack/structure), and each change's `design.md` (decisions and alternatives), plus `eval/FAILURE_ANALYSIS.md` and `eval/BASELINE_COMPARISON.md` (real measured results). This change assembles those into the reader-facing entry point PLANNING.md's README section asks for - it does not invent new content.

## Goals / Non-Goals

**Goals:**
- One README a reviewer can read start to finish to understand the project, run it, and see real results - no invented numbers, only what `eval/results/` and the archived changes' design docs actually contain.
- Cover every bullet in PLANNING.md's README Must Explain list.
- A demo script section that matches what the CLI actually does (to be confirmed against a live run in the final verification pass, not assumed).

**Non-Goals:**
- Rewriting or duplicating `PLANNING.md`/`CLAUDE.md` wholesale - the README summarizes and links to them for full depth, per CLAUDE.md's Where the Plan Lives section already doing the same thing for internal docs.
- Generating diagrams as image files - `ARCHITECTURE.md` uses a text/mermaid-style diagram, consistent with the rest of the repo's plain-markdown documentation.

## Decisions

**The README pulls its "actual results" and "what alternatives were considered" sections directly from `eval/FAILURE_ANALYSIS.md` and `eval/BASELINE_COMPARISON.md` rather than re-deriving numbers.** Those files are the already-verified, real measurement record; restating them in the README risks transcription drift from the source of truth. The README summarizes and links to them for full detail.

**`ARCHITECTURE.md` is a separate file from `README.md`.** README stays readable end-to-end for someone evaluating the project; architecture detail (component diagram, data flow, the "embeddings are not the source of truth" statement) is substantial enough to warrant its own file, matching CLAUDE.md's Repo Structure section which already lists `ARCHITECTURE.md` as a planned top-level file.

**The demo script is verified live as part of this project's final testing pass, not written speculatively and left unchecked.** A demo script that doesn't match actual CLI behavior would be worse than no demo script - this is called out explicitly in tasks.md rather than assumed correct on the first draft.

## Risks / Trade-offs

- [README could grow too long to be a good entry point] → Mitigated by linking to `PLANNING.md`, `CLAUDE.md`, and the eval writeups for depth rather than inlining everything.

## Open Questions

None.
