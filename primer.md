# CSDL Primer — A Human-Writable Guide

**Version:** 1.0
**Author:** Mark Atwood
**Date:** 2026-02-09
**Status:** Companion Document (Informative)
**Companion to:** CJK Stroke Description Language (CSDL) Specification v1.0 [CSDL]

---

## Purpose

This document is a compact, tutorial-style guide to reading and
writing CSDL files. It is informative, not normative. All
definitions, constraints, and conformance requirements live in
[CSDL]. When this primer and [CSDL] disagree, [CSDL] wins.

The primer emphasizes one-line character definitions and defers
to component references wherever possible. Any valid file written
using the patterns in this guide is a valid CSDL file.

**Core principle:** Most CJK characters are compositions of known
components. CSDL encodes *structure*, not strokes. You only drop
to stroke-level definitions for leaf components (radicals and
primitives). Everything else is naming parts and saying how they
fit together.

All section references (§) refer to [CSDL] unless otherwise noted.

---

## 1. Character Line Format

The inline form (§11) is the primary vehicle:

```
CHAR PINYIN = LAYOUT(parts) [metadata]
```

Examples (real characters, one line each):

```
明 ming2 = LR(日, 月)
想 xiang3 = TB(相, 心)
問 wen4 = SUR(門, 口)
侍 si4 = LR(亻, 寺, 4/8)
草 cao3 = TB(艹, TB(日, 十), 3/9)
林 lin2 = LR(木, 木)
器 qi4 = GRID(口, 口, 口, 口)
```

If the components are already defined, most characters are one
line.

---

## 2. Layout Operators (Quick Reference)

Mnemonic order: split → surround → overlay → grid. All eight
operators are defined normatively in §8; this table is a
convenience summary.

| Op | Meaning | Default Split | Example |
|----|---------|---------------|---------|
| `LR(a, b)` | Left-Right | 6/6 | `LR(日, 月)` |
| `TB(a, b)` | Top-Bottom | 6/6 | `TB(相, 心)` |
| `LR3(a, b, c)` | 3-way horiz | 4/4/4 | `LR3(亻, 木, 木)` |
| `TB3(a, b, c)` | 3-way vert | 4/4/4 | `TB3(艹, 口, 木)` |
| `SUR(a, b)` | Surround | full, inset 2 | `SUR(囗, 或)` |
| `OVR(a, b)` | Overlay | — | `OVR(十, 口)` |
| `GRP(a, b…)` | Group 2+ | — | `GRP(一, 口, 木)` |
| `GRID(a,b,c,d)` | 2×2 grid | 6/6, 6/6 | `GRID(口, 口, 口, 口)` |

Splits are proportional ratios (§5). Default is even.
Override: `LR(亻, 寺, 4/8)`. Values summing to 12 align with
grid boundaries but any positive integers work (the renderer
divides proportionally). Common values: 6/6, 4/8, 5/7, 3/9,
4/4/4, 3/6/3.

SUR side specifiers (when not full enclosure): `tl` `tr` `top`
`right` `left` `bot` `bl` `br`. Example: `SUR(广, 木, tl)` =
shelter from top-left.

---

## 3. Components: Name Once, Use Everywhere

Components are the CJK characters or radicals themselves (§10).
Reference by character or pinyin alias.

Aliases (ASCII names for radicals, per §10.7):
```
@alias kou3 = 口
@alias mu4 = 木
@alias ren2.left = 亻
@alias shui3.left = 氵
```

After aliasing, `kou3` and `口` are interchangeable everywhere.

Positional variants use dot notation (§10.5):
- `心` = standalone heart
- `心.left` = 忄 (left-side variant)
- `心.bot` = bottom variant

Common tags: `left` `right` `top` `bot` `inner` `outer` `simp`
`alt`.

---

## 4. Defining Leaf Components (Strokes)

Only needed for primitives that cannot be decomposed further.
Two-line minimum. See §7 and §10 for full syntax.

```
@comp 口
build: s1 s2 s3
s1 = S(shu [3,2] [3,10] 1)
s2 = S(heng-zhe [3,2] [9,2] [9,10] 1)
s3 = S(heng [3,10] [9,10] 1)
@end
```

Stroke syntax: `S(name [x,y] [x,y]… width)`. Coordinates are on
the 12×12 grid (§5). Width: 0=hairline, 1=normal, 2=bold.

---

## 5. Stroke Names (38 Total)

12 base strokes (§7.1):

| Name | Description |
|------|-------------|
| `heng` | Horizontal → |
| `shu` | Vertical ↓ |
| `pie` | Left-falling ↙ |
| `na` | Right-falling ↘ |
| `dian` | Dot |
| `ti` | Rising ↗ |
| `gou` | Hook |
| `wan` | Bend (curve) |
| `zhe` | Sharp turn |
| `xie` | Slant |
| `wo` | Reclining hook |
| `quan` | Circle/loop ○ |

26 compound strokes (§7.2, [CSDL] Appendix C) = segments joined
at turns. Name = segment sequence. Points = segments + 1.

| Folds | Examples | Points |
|-------|----------|--------|
| 1 | `heng-zhe`, `shu-gou`, `pie-dian` | 3 |
| 2 | `heng-zhe-gou`, `shu-wan-gou` | 4 |
| 3 | `heng-zhe-wan-gou`, `shu-zhe-zhe-gou` | 5 |
| 4 | `heng-zhe-zhe-zhe-gou` | 6 |

---

## 6. Expression-Form Components (Compositions)

When a component is just a layout of other components:

```
@comp 相
build: from_expr
LR(木, 目, 5/7)
@end
```

This is equivalent to writing out all strokes, but much shorter.
See §10.3.

---

## 7. Transforms (Rare, 3 Types)

Values are /12 fractions (12=100%). See §9.

| Op | Meaning | Example |
|----|---------|---------|
| `sc(x, sx=N, sy=N)` | Scale | `sc(口, sx=8, sy=8)` = 2/3 size |
| `sh(x, dx=N, dy=N)` | Shift | `sh(口, dx=2, dy=1)` = right 2, down 1 |
| `sk(x, kx=N, ky=N)` | Skew | `sk(木, kx=1, ky=0)` = slight lean |

Compose inside-out: `sh(sc(口, sx=8, sy=8), dx=4, dy=4)` =
shrink then move.

---

## 8. Metadata (Optional, Trailing)

Append to any character line (§11.3, §13):

```
明 ming2 = LR(日, 月) rad:72 sc:8
國 guo2 = SUR(囗, 或) ortho:Hant rad:31 sc:11
```

| Tag | Meaning |
|-----|---------|
| `rad:N` | Kangxi radical (1–214) |
| `sc:N` | Stroke count |
| `freq:N` | Frequency rank |
| `ortho:TAG` | Writing tradition (Hant, Hans, Jpan, Kore…; see [CSDL] Appendix E) |
| `x-KEY:VAL` | Extension metadata |

Multiple ortho tags: `ortho:Hant,Jpan`.

---

## 9. Build Order (Stroke Order)

**Explicit** (in `@comp`/`@char` blocks): `build: s1 s2 s3 s4` —
strokes drawn in listed order (§12.1).

**Definition order** (stroke-form block, no `build:` line): strokes
are drawn in the order their definitions appear in the block (§12.1).

**Implicit** (from expression structure, `build: from_expr`;
§12.2):

1. Top before bottom
2. Left before right
3. Outside before inside
4. GRID: reading order (TL, TR, BL, BR)

**Closing stroke** for enclosures (§12.4): `close: s3`
moves that stroke after the inner component.

```
@comp 囗
build: s1 s2 s3
close: s3
s1 = S(shu [2,1] [2,11] 1)
s2 = S(heng-zhe [2,1] [10,1] [10,11] 1)
s3 = S(heng [2,11] [10,11] 1)
@end
```

---

## 10. Complete Minimal File

```
@csdl 1.0

# Aliases
@alias kou3 = 口
@alias ri4 = 日
@alias yue4 = 月

# Leaf components (strokes)
@comp 口
build: s1 s2 s3
s1 = S(shu [3,2] [3,10] 1)
s2 = S(heng-zhe [3,2] [9,2] [9,10] 1)
s3 = S(heng [3,10] [9,10] 1)
@end

@comp 日
build: s1 s2 s3 s4
s1 = S(shu [3,1] [3,11] 1)
s2 = S(heng-zhe [3,1] [9,1] [9,11] 1)
s3 = S(heng [3,6] [9,6] 1)
s4 = S(heng [3,11] [9,11] 1)
@end

@comp 月
build: s1 s2 s3 s4
s1 = S(pie [3,1] [1,11] 1)
s2 = S(heng-zhe-gou [3,1] [9,1] [9,11] [3,11] 1)
s3 = S(heng [4,4] [8,4] 1)
s4 = S(heng [4,7] [8,7] 1)
@end

# Characters (one line each)
明 ming2 = LR(日, 月) rad:72 sc:8
問 wen4 = SUR(門, 口) rad:30 sc:11
```

---

## 11. Reading CSDL: A Cheat Sheet

Ask these questions in order:

1. **What character?** The CJK glyph and pinyin on the left of `=`.
2. **How is it arranged?** The layout operator: LR, TB, SUR, etc.
3. **What are the parts?** The arguments inside the parentheses.
4. **Are proportions even?** If no split given, yes. If split given, read it.
5. **Any metadata?** Trailing `rad:` `sc:` `ortho:` tags.

If a part is not defined in the current file, either it is a known
radical/component defined elsewhere, or it needs a `@comp` block
to define it from strokes.

The typical workflow: define the ~214 Kangxi radical components
once (see [CSDL] Appendix B and Appendix E), then describe
thousands of characters as one-line compositions referencing those
components.

---

## 12. Quick Reference Card

```
LAYOUT:   LR TB LR3 TB3 SUR OVR GRP GRID
SPLIT:    proportional ratio (values summing to 12 preferred)
SUR SIDE: full tl tr top right left bot bl br  (default: full)
XFORM:    sc(_, sx=, sy=)  sh(_, dx=, dy=)  sk(_, kx=, ky=)
STROKE:   S(name [x,y]... width)   width: 0/1/2
GRID:     12×12, origin top-left   (/24 for fine detail)
VARIANT:  name.tag  (心.left, 木.top)
META:     rad: sc: freq: ortho: x-*:
```

---

## References

**[CSDL]**
CJK Stroke Description Language (CSDL) Specification, Version 1.0 Draft, 2026-02-09.
