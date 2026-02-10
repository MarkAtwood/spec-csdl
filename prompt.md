# CSDL Spec Restart Prompt

## Problem

There is no standard that describes how CJK ideographic characters
are structurally built from strokes and components. Unicode encodes
identity, not structure. IDS is symbolic, not geometric. Fonts
store flattened outlines with no semantics. Pedagogical databases
are annotations, not grammars.

CSDL fills the missing layer: a constructive, non-Turing DSL that
can describe how any CJK character is composed from strokes,
reusable components, and spatial layout operators.

## Target Output

A single document in W3C personal-note / RFC style. ASCII text
except for component names, which are either Unicode characters or
ASCII pinyin with vowel-number tone markers (e.g., kou3, ming2).

## Non-Turing Constraints

- No loops, variables, conditionals, recursion, or macros.
- A character is a finite DAG of nodes.
- Evaluation is a single pass: resolve refs, compute boxes, place
  children, emit stroke geometry.
- All operator sets (strokes, layouts, transforms) are closed and
  enumerated. Unknown operators MUST be rejected.
- Component references MUST be acyclic.
- Deterministic: same input always produces same output.

## Coordinate System

- Box divided into 12ths. Integer coordinates 0-12.
- Origin: top-left. X right, Y down.
- [0,0] = top-left, [12,12] = bottom-right, [6,6] = center.
- 12 chosen because it divides by 2, 3, 4, 6 (halves, thirds,
  quarters, sixths all land on integers).
- Optional /24 override for complex components.
- Stroke width: integer grid units (0=hairline, 1=normal, 2=bold).
- Child boxes inherit their own [0,0]-[12,12] coordinate space.

## Terseness Goal

~85% of characters described in one line:

    U+660E ming2 = LR(日, 月)
    U+554F wen4  = SUR(門, 口)
    U+60F3 xiang3 = TB(相, 心)

Complex components use block form:

    @comp 口
    build: s1 s2 s3
    s1 = S(shu [3,2] [3,10] 1)
    s2 = S(heng-zhe [3,2] [9,2] [9,10] 1)
    s3 = S(heng [3,10] [9,10] 1)
    @end

## Component Naming

- Unicode character: 口, 木, 氵
- ASCII pinyin with tone number: kou3, mu4, shui3pang2
- @alias kou3 = 口
- Positional variants: 心.bot, 心.left, 阜.left, 邑.right

## 11 Base Strokes

    heng shu pie na dian ti gou wan zhe xie wo

## 26 Compound Strokes (enumerated, closed set)

Single-fold (12): heng-zhe, heng-pie, heng-gou, shu-zhe, shu-wan,
  shu-ti, shu-gou, pie-zhe, pie-dian, wan-gou, xie-gou, wo-gou

Double-fold (8): heng-zhe-zhe, heng-zhe-wan, heng-zhe-ti,
  heng-zhe-gou, heng-xie-gou, shu-zhe-zhe, shu-zhe-pie,
  shu-wan-gou

Triple-fold (5): heng-zhe-zhe-zhe, heng-zhe-zhe-pie,
  heng-zhe-wan-gou, heng-pie-wan-gou, shu-zhe-zhe-gou

Quadruple-fold (1): heng-zhe-zhe-zhe-gou

Total: 37 stroke types (11 base + 26 compound).

Point count rule: total_points = sum(min_points) - (N-1)

## 8 Layout Operators

    LR(a, b [, split])           left-right, default 6/6
    TB(a, b [, split])           top-bottom, default 6/6
    LR3(a, b, c [, split])      three-part horizontal, default 4/4/4
    TB3(a, b, c [, split])      three-part vertical, default 4/4/4
    SUR(a, b [, side, inset])   surround, default full/inset=2
    OVR(a, b)                   overlay
    GRP(a, b, ..., h)           group (2-8 children, avoids nested OVR)
    GRID(a, b, c, d)            2x2 grid

Split values must sum to 12.

SUR side values: full, tl, tr, top, left, bot, bl

## 3 Transform Operators

    sc(expr, sx=N, sy=N)    scale (N out of 12)
    sh(expr, dx=N, dy=N)    shift (signed grid units)
    sk(expr, kx=N, ky=N)    skew (signed grid units)

All params bounded integers, range -12 to 24.

## Build Order

Explicit via build: line in @comp blocks.
Implicit via standard rules: top-before-bottom, left-before-right,
outside-before-inside, inside-before-closing-stroke.

## IDS Mapping

    ⿰ LR  ⿱ TB  ⿲ LR3  ⿳ TB3  ⿴ SUR(full)  ⿵ SUR(top)
    ⿶ SUR(bot)  ⿷ SUR(left)  ⿸ SUR(tl)  ⿹ SUR(tr)
    ⿺ SUR(bl)  ⿻ OVR

## Appendix Requirements

A. IDS operator mapping table (compact, 12 rows)
B. Complete Kangxi 214 radical registry: rad#, char, pinyin,
   strokes, meaning, variants, typical position(s)
C. Compound stroke enumeration with registry IDs C01-C26
D. Complete example file (aliases, component defs, inline chars)

## Conformance Levels

Level 1 (Parser): parse, validate acyclicity, resolve refs.
Level 2 (Renderer): compute boxes, emit stroke geometry.
Level 3 (Full): stroke expansion to filled outlines.

## Spec Structure

    1.  Introduction (motivation, goals, scope, design principles)
    2.  Conformance (RFC 2119, three levels)
    3.  Terminology
    4.  Data Model
    5.  Coordinate System
    6.  Expression Grammar (EBNF)
    7.  Stroke Primitives (base + compound enumeration)
    8.  Layout Operators
    9.  Transform Operators
    10. Component Definitions (block form, inline form, variants)
    11. Character Definitions (one-line form, block form, metadata)
    12. Build Order Derivation (explicit, implicit, algorithm)
    13. Extensibility (safe additions, forbidden additions)
    14. Security Considerations (no execution, bounded evaluation)
    15. References
    Appendix A-D

## Key Design Decisions Already Made

- 12ths grid, not 10ths (better divisibility)
- GRP operator to avoid nested OVR
- Compound strokes enumerated as named primitives (not composed
  at runtime via a join operator)
- Component variants via dotted names (心.bot, 心.left)
- Variant selection is renderer RECOMMENDATION, not requirement
- Radical 74/130 (月 moon vs meat) disambiguation is author's
  responsibility via pinyin labels
- Radical 163/170 (阝 right=city vs left=mound) modeled as
  separate components via positional variant names
- File format is UTF-8 text, line-oriented
- Metadata is informational, does not affect evaluation
