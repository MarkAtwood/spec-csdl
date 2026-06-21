# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:970c3bf2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->


## Build & Test

```bash
# Run Level 1 parser tests
python3 test_csdl.py

# Validate a CSDL file
python3 csdl.py <file.csdl>  # exit 0=valid, 1=invalid
```

## Architecture Overview

**CSDL (CJK Stroke Description Language)** is a non-Turing DSL for describing how CJK characters are composed from strokes and components.

Key files:
- `csdl-spec.md` - Normative specification (W3C/RFC style)
- `primer.md` - Informative tutorial for humans
- `prompt.md` - Design decisions summary (for AI context)
- `csdl.py` - Level 1 reference parser (~670 lines Python)
- `test_csdl.py` - 22 test cases for parser validation

Conformance levels:
- **Level 1 (Parser)**: Syntax + semantic validation (implemented)
- **Level 2 (Renderer)**: Bounding box computation, stroke placement
- **Level 3 (Full)**: Stroke expansion to filled outlines

## Conventions & Patterns

- 12×12 grid coordinate system (origin top-left)
- 38 strokes: 12 base + 26 compound (closed registry)
- 8 layout operators: LR, TB, LR3, TB3, SUR, OVR, GRP, GRID
- 3 transform operators: sc, sh, sk
- Component names: CJK characters or pinyin with tone (e.g., `kou3`, `心.left`)
- One-line character definitions: `明 ming2 = LR(日, 月)`
- Block form for stroke-level components

## Closed Beads (Context)

- **CSDL-5nw**: Added `quan` (circle/loop) as 12th base stroke
- **CSDL-6b2**: Appendix F - Japanese kana stroke analysis
- **CSDL-fq9**: Made ortho tags accept any ISO 15924 code
- **CSDL-do9**: Expanded SUR operator documentation
- **CSDL-2nh**: Level 1 reference parser
