# CSDL Implementor's Checklist

**Version:** 1.0
**Date:** 2026-02-09
**Status:** Companion Document
**Companion to:** CJK Stroke Description Language (CSDL) Specification v1.0 [CSDL]

---

## Purpose

This document collects every item that the CSDL specification
leaves to renderers, toolchains, or authors. It contains no new
normative text. Every entry is a cross-reference to the section
of [CSDL] where the decision is defined. The purpose is to give
implementors a single checklist of choices they must make.

All section references (§) refer to [CSDL] unless otherwise noted.

---

## 1. Explicitly Out of Scope

These concerns are not addressed by CSDL at all. The
specification makes no statements about them and future versions
are not expected to add them.

| Topic                                      | Reference       |
|--------------------------------------------|-----------------|
| Glyph rendering (anti-aliasing, hinting, rasterization) | §1.3 |
| Font metrics (advance widths, kerning, vertical metrics) | §1.3 |
| Text layout (line breaking, justification, bidi)         | §1.3 |
| Character encoding or identification (handled by Unicode)| §1.3 |
| Stroke animation or temporal sequencing for pedagogy     | §1.3 |
| Aesthetic or calligraphic style variation                | §1.3 |
| File import, include, or cross-file references           | §4.2.2 |
| Kana, Hangul, or other non-ideographic scripts           | §App E.1 |
| Calligraphic and historical radical variants             | §App B  |
| Component definitions for Kangxi radicals (data, not spec)| §App B |

---

## 2. Implementation-Defined (Parser/Tooling)

These are choices a parser or toolchain must make. The spec
requires correct rejection of invalid input but does not constrain
how these decisions are made.

| Decision                                   | Reference       |
|--------------------------------------------|-----------------|
| Error recovery strategy (stop-at-first, collect-all, partial output) | §2.3 |
| Error reporting format (message text, structured JSON, error codes, line/column) | §2.3 |
| Capacity limits (SHOULD support the full CJK Unified Ideographs repertoire) | §14 |
| Multi-file concatenation and library management | §4.2.2     |
| NFC detection and rejection of non-NFC input | §4.2          |
| Mapping of stroke width values (0, 1, 2) to concrete pixel or em widths | §5.4 |
| Whether to warn on duplicate component names | §4.5          |
| Whether to warn on unknown metadata fields  | §13.1          |
| Whether to warn on unknown orthography tags  | §13.1         |
| Whether to warn on unknown minor version numbers | §4.2      |
| Rejection of stroke invocations with wrong coordinate count  | §7.3, §7.4 |
| Whether to warn on stroke geometry inconsistent with stroke name | §7.4 |

---

## 3. Renderer Discretion (MAY/SHOULD)

These are decisions a Level 2 or Level 3 renderer MAY or SHOULD
make. Two conformant renderers may produce visually different
output from the same CSDL input due to these choices. The
evaluated stroke geometry (positions and connectivity) is
deterministic; visual presentation is not.

| Decision                                   | Reference       |
|--------------------------------------------|-----------------|
| Output format (filled outlines, SVG paths, bitmaps, other) | §1.3 |
| Aesthetic proportion adjustment within layout operators   | §1.4, Principle 2 |
| Positional variant substitution (e.g., 心 → 心.left based on position) | §1.4 Principle 3, §10.5 |
| Concrete stroke width mapping (hairline, normal, bold to pixels/ems) | §5.4 |
| Visual shape of `dian` stroke (rounded, teardrop, triangular) | §7.1 |
| Interpolation of curved strokes (`wan`, `gou`, `wo`) between coordinate points | §7.1 |
| Orthography-based definition selection when multiple definitions exist | §4.7.2, §App E.5 |
| Orthography-based definition filtering     | §4.7.2          |
| Selection between implicit (@comp) and explicit (@char) definitions with distinct ortho tags | §10.6 |
| Fallback when no ortho-matched definition exists | §4.7.2     |
| Treatment of unknown `x-` orthography tags as opaque filter keys | §13.3 |
| Expansion of stroke geometry to filled outlines (Level 3) | §2.2 |
| Handling of `x-` extension strokes (render as fallback, ignore, or custom) | §7.5 |

---

## 4. Author Responsibility

These are decisions or obligations that fall on the CSDL file
author, not on parsers or renderers. A conformant parser is not
required to validate these; incorrect authoring may produce
unexpected but syntactically valid results.

| Decision                                   | Reference       |
|--------------------------------------------|-----------------|
| Disambiguation of graphically identical radicals (e.g., 月 moon vs 肉 meat) | §1.4 Principle 4, §App B |
| Ensuring NFC consistency in file text       | §4.2           |
| Choosing the correct positional variant name vs. relying on renderer substitution | §10.5 |
| Providing a `close:` marker for enclosure components where pedagogically correct stroke order matters | §12.4 |
| Geometric plausibility of compound stroke coordinates (names are labels, not constraints) | §7.4 |
| Pinyin alias uniqueness for radicals with colliding readings | §App B |
| Selecting the most specific applicable orthography tag | §App E.4 |
| Noting non-standard stroke usage in extended scripts via `x-` metadata | §13.3 |

---

## 5. Deterministic by Specification

For contrast, these properties are fully determined by the spec.
Two conformant implementations given the same input MUST produce
identical results for these.

| Property                                   | Reference       |
|--------------------------------------------|-----------------|
| Stroke geometry (positioned line segments from coordinates) | §2.2 Level 2 |
| Bounding box computation for all nodes      | §2.2 Level 2  |
| Child box inheritance (each child gets its own 12×12 space) | §5.2 |
| Layout operator space division (proportional splits)     | §8       |
| SUR inset application (covered sides only)  | §8.6           |
| Transform composition order (inside-out)    | §9.1           |
| Transform anchor point (center, `[6,6]`)    | §9.1, §9.2     |
| Transform parameters use /12 grid even in /24 blocks | §9.1    |
| Stroke coordinate count must match named stroke type | §7.3, §7.4 |
| Explicit build order (stroke sequence from `build:` line) | §12.1 |
| Default build order when `build:` omitted in stroke form (definition order) | §12.1 |
| Implicit build order when no `close:` marker present | §12.2 |
| Implicit build order when `close:` marker present | §12.2, §12.4 |
| Component reference resolution (last-definition-wins for duplicates) | §4.5 |
| Alias resolution (bidirectional equivalence) | §10.7         |
| Acyclicity enforcement                      | §4.4           |
| Closed operator sets (reject unknown strokes, layouts, transforms) | §1.2, §6.9 |

---

## References

**[CSDL]**
CJK Stroke Description Language (CSDL) Specification, Version 1.0 Draft, 2026-02-09.
