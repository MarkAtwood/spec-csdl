# CSDL: A Construction Grammar for Chinese Characters

## The Problem: Nobody Describes How Characters Are Built

Chinese characters (and their Japanese, Korean, and Vietnamese cousins, collectively "CJK") exist in several digital representations, and every single one of them throws away structural information.

**Unicode** assigns each character a code point. It tells you "this is character U+660E" but says nothing about the fact that U+660E is composed of two sub-parts arranged side by side. It encodes *identity*, not *structure*.

**Ideographic Description Sequences (IDS)**, a Unicode annex, go one step further. IDS can express "U+660E is ⿰日月" (meaning: left-right arrangement of 日 and 月). But IDS is purely topological. It says *left-right*, not *where the dividing line falls*, not *what strokes make up each part*, not *what coordinates those strokes occupy*. It's a labeled tree with no geometry.

**Font formats** (OpenType, TrueType) store the actual rendered outlines as cubic or quadratic Bézier curves. But the compilation process that produces those outlines destroys all component-level structure. You cannot look at a font's glyph data and recover "this character is two sub-parts arranged left-right." The semantic structure has been flattened into raw curves.

**Pedagogical databases** (CHISE, Unihan, various stroke-order databases) annotate characters with structural metadata, but these are informational labels, not constructive descriptions. They're field notes, not blueprints.

CSDL (CJK Stroke Description Language) occupies the gap between all of these. It is a constructive, deterministic language that takes stroke primitives, reusable named components, and spatial layout operators as input and produces positioned stroke geometry as output. Given a CSDL expression, you can evaluate it and get an unambiguous geometric description of a character. It is, essentially, a build specification for ideographic characters.

## Background: How CJK Characters Work (Minimum Viable Version)

A reader who has never studied Chinese needs exactly three concepts to follow the rest of this article.

**Strokes.** Every CJK character is drawn with a sequence of individual pen strokes. A horizontal line is a stroke. A vertical line is a stroke. A diagonal falling to the left is a stroke. There are about 11 basic stroke types, and they combine at junction points into about 26 compound strokes (a horizontal line that turns into a vertical line is one compound stroke, drawn without lifting the pen). The total inventory is 37 named stroke types. That's it. Every character in every CJK script is drawn from this set.

**Components.** Characters are built from reusable sub-parts. The character meaning "bright" (明) is composed of two sub-parts: 日 (sun) on the left and 月 (moon) on the right. Each sub-part is itself a small character made of strokes, and each can appear inside many different characters. These reusable sub-parts are called components. Some components change shape depending on where they appear within a character (squeezed thinner when on the left, abbreviated when on top, etc.), and these shape variants are called positional variants.

**Radicals.** Of the roughly 98,000 encoded CJK characters, each is traditionally classified under one of 214 categories called Kangxi radicals (named after a Chinese dictionary from 1716). This is a classification system, not a structural one, but CSDL carries the radical number as metadata because it's useful for lookup.

## Language Design: What CSDL Is and Isn't

CSDL is a domain-specific language with some unusual properties that are worth stating up front, because they define its character.

**It is constructive.** A CSDL expression can be evaluated to produce geometry. It's not a description or annotation; it's a program (in the loosest sense) that outputs positioned strokes.

**It is deterministic.** Same input, same output. Always. No randomness, no implementation-defined behavior in evaluation, no context-sensitivity.

**It is non-Turing.** There are no loops, no variables, no conditionals, no recursion, no macros. A character definition is a finite directed acyclic graph of nodes. Evaluation is a single pass: resolve references, compute bounding boxes, place children, emit strokes. Evaluation always terminates. This is a *hard* design constraint that the spec explicitly forbids future versions from relaxing.

**It is closed.** Every operator set (strokes, layouts, transforms) is enumerated and finite. A conformant parser must reject any operator it doesn't recognize. This prevents dialect fragmentation: if a parser accepts a file, every other conformant parser will too.

**It is not a font format.** CSDL output is a tree of positioned strokes in a coordinate space. How you render those strokes (anti-aliased outlines, SVG paths, bitmap, calligraphic brush simulation) is your problem. CSDL describes structure, not aesthetics.

**It is not a text layout engine.** Line breaking, justification, kerning, advance widths: all out of scope.

## File Format

A CSDL file is UTF-8, line-oriented plain text. The conventional extension is `.csdl`. Files begin with an optional version declaration and an optional orthography declaration:

```
@csdl 1.0
@ortho Hant
```

The version declaration follows semantic versioning with a strict contract: minor versions can add metadata fields and orthography tags, but adding a new stroke name or layout operator requires a major version bump (because the closed-set enforcement means a v1 parser would reject the new name).

The orthography declaration sets a default writing tradition for the file (here, Traditional Chinese). Individual definitions can override it. More on orthography below.

After the declarations come three kinds of definitions: aliases, components, and characters. Comments begin with `#`.

## The Coordinate System

CSDL divides every bounding box into a 12×12 grid. The origin `[0,0]` is the top-left corner; `[12,12]` is the bottom-right; `[6,6]` is the center. Twelve was chosen because it's evenly divisible by 2, 3, 4, and 6, so halves, thirds, quarters, and sixths all land on integer coordinates without rounding.

When a layout operator subdivides a bounding box (putting one component on the left, another on the right), each child region becomes its own fresh `[0,0]` to `[12,12]` space. Coordinates are always local to the containing box.

For components that need finer positioning, a `/24` override doubles the grid resolution to 24×24 within a single component block. This is the exception; most definitions use the default grid.

Stroke width takes one of three integer values: 0 (hairline), 1 (normal), 2 (bold). The mapping from these values to actual rendered widths is up to the implementation.

## Strokes

Every stroke is invoked with the `S()` function:

```
S(heng [2,4] [10,4] 1)
```

This draws a `heng` (horizontal) stroke from grid point [2,4] to [10,4] at normal width. The 11 base strokes are: `heng` (horizontal), `shu` (vertical), `pie` (left-falling diagonal), `na` (right-falling diagonal), `dian` (dot), `ti` (rising), `gou` (hook), `wan` (bend), `zhe` (sharp turn), `xie` (slant), and `wo` (reclining hook). The names are romanized Chinese (pinyin) because that's what the calligraphic tradition uses.

Compound strokes are named by concatenating their constituent segments with hyphens. `heng-zhe` is a horizontal stroke that makes a sharp turn downward. `shu-wan-gou` is a vertical stroke that bends right and then hooks. The naming is systematic: read the hyphenated name left to right and you get the stroke's trajectory.

Compound strokes require more coordinate points because each junction is a point. The formula is simple: a compound stroke with N segments needs N+1 points (each segment shares its endpoint with the next segment's start). So `heng` needs 2 points, `heng-zhe` needs 3, `heng-zhe-zhe` needs 4, and so on up to the single five-segment compound `heng-zhe-zhe-zhe-gou` which needs 6 points.

The compound stroke names are semantic labels, not geometric constraints. The parser does not check whether the coordinates you provide for a `heng` (horizontal) stroke actually form a horizontal line. Two renderers given the same coordinates must produce the same line segments regardless of whether those segments "look like" the named stroke type. The name tells you *what kind of stroke it is* for classification and stroke-counting purposes; the coordinates tell you *where to draw it*.

The full inventory is 37 strokes: 11 base, 12 single-fold compounds, 8 double-fold, 5 triple-fold, and 1 quadruple-fold.

## Layout Operators

Layout operators are how components get arranged relative to each other. There are eight, and they cover the spatial relationships that CJK characters actually use.

**LR (Left-Right)** divides the bounding box into two side-by-side regions. `LR(日, 月)` puts 日 on the left and 月 on the right. By default the split is 50/50, but you can specify proportions: `LR(亻, 寺, 4/8)` gives 4 grid units to the left part and 8 to the right. Split values are proportional ratios; they're not required to sum to 12, though values that do align neatly with grid boundaries.

**TB (Top-Bottom)** is the vertical equivalent. `TB(相, 心)` stacks 相 on top, 心 on bottom.

**LR3 and TB3** handle three-way splits (three components side by side, or three stacked). Default split is equal thirds.

**SUR (Surround)** handles enclosure, the most structurally interesting layout. `SUR(門, 口)` places 口 inside 門. The surround operator takes an optional `side` parameter specifying which sides the outer component covers: `full` (all four sides, like 囗), `tl` (top and left, like 广), `top` (three sides open at bottom), `left`, `right`, `bot`, `bl`, `br`, `tr`. An `inset` parameter controls how many grid units the inner component is pushed inward from the covered sides. On uncovered sides, the inner component extends to the parent edge.

**OVR (Overlay)** superimposes two components in the same bounding box. Used for characters where parts overlap rather than sitting in separate spatial regions.

**GRP (Group)** is OVR for more than two components, avoiding deep nesting.

**GRID** divides the bounding box into a 2×2 grid with four children in reading order (top-left, top-right, bottom-left, bottom-right), with optional horizontal and vertical split parameters.

Layout operators nest. `TB(艹, TB(日, 十), 3/9)` is a top-bottom split where the bottom half is itself a top-bottom split. This handles the common pattern of characters with three vertical layers where the top layer is narrow.

## Transform Operators

Three transform operators modify the geometry of a child expression:

**sc (scale)** scales a component. Scale factors are expressed as fractions of 12: `sx=12` means 100%, `sx=6` means 50%, `sx=18` means 150%. Scaling is anchored at the center of the bounding box.

**sh (shift)** translates a component by a specified number of grid units. `sh(口, dx=2, dy=1)` moves 口 two units right and one down.

**sk (skew)** applies a shear transformation. `sk(木, kx=1, ky=0)` tilts 木 slightly to the right.

Transforms compose inside-out: `sh(sc(口, sx=8, sy=8), dx=4, dy=4)` first scales 口 to 2/3 size, then shifts the result toward the bottom-right corner. This is standard function composition; implementations must not reorder transforms.

All transform parameters are bounded integers between -12 and 24. The upper bound is 2× the grid dimension, which is sufficient for all known composition patterns. Exceeding this range is treated as a modeling error.

## Components: Reusable Sub-Structures

Components are defined in block form between `@comp` and `@end` markers. There are two flavors.

**Stroke form** defines a component from explicit stroke invocations:

```
@comp 口
build: s1 s2 s3
s1 = S(shu [3,2] [3,10] 1)
s2 = S(heng-zhe [3,2] [9,2] [9,10] 1)
s3 = S(heng [3,10] [9,10] 1)
@end
```

This defines 口 (mouth) as three strokes: a vertical line on the left, a horizontal-turn stroke forming the top and right sides, and a horizontal line along the bottom. The `build:` line specifies stroke order (the sequence in which the strokes should be drawn).

**Expression form** defines a component by composing other components:

```
@comp 相
build: from_expr
LR(木, 目, 5/7)
@end
```

This defines 相 as a left-right arrangement of 木 and 目, with 木 getting 5 grid units and 目 getting 7. Expression-form components exist for reuse and readability; they're structurally equivalent to inlining the expression everywhere it's referenced.

Components support **positional variants** via dotted names. The character 心 (heart) looks different when it appears at the bottom of a character versus on the left side. CSDL handles this with separate component definitions:

```
@comp 心
build: s1 s2 s3 s4
...
@end

@comp 心.left
build: s1 s2 s3
...
@end
```

When a character definition references `心`, a renderer may substitute `心.left` or `心.bot` based on the structural position. This substitution is recommended but not required. An author who needs a specific variant should use the variant name explicitly.

## Character Definitions

Characters can be defined inline (one line) or in block form.

**Inline form:**

```
U+660E ming2 = LR(日, 月) rad:72 sc:8
```

This defines Unicode code point U+660E (明, "bright"), with the pinyin pronunciation `ming2`, as a left-right composition of 日 and 月. The metadata fields `rad:72` (Kangxi radical 72, 日) and `sc:8` (8 total strokes) are informational and do not affect evaluation.

**Block form** is used for characters defined directly from strokes rather than from components:

```
@char U+6C38 yong3
build: s1 s2 s3 s4 s5
s1 = S(dian [6,1] [6,3] 1)
s2 = S(heng-gou [3,3] [9,3] [7,6] 1)
s3 = S(shu-gou [6,3] [6,10] [4,8] 1)
s4 = S(pie [6,6] [2,11] 1)
s5 = S(na [6,6] [10,11] 1)
rad: 85
sc: 5
@end
```

This defines 永 (yong3, "eternal"), a character famous in calligraphy because it contains representatives of all the basic stroke types, from five explicit strokes with their coordinates.

The pinyin name (the romanized pronunciation with tone number) serves as a human-readable label. It also provides an ASCII handle for the character in contexts where Unicode input isn't available.

## Aliases

Alias definitions bind an ASCII pinyin name to a Unicode character, allowing either to be used interchangeably in expressions:

```
@alias kou3 = 口
@alias mu4 = 木
@alias shui3.left = 氵
```

After these definitions, `kou3` and `口` are the same thing everywhere in the file. Aliases exist so that authors can write CSDL using only ASCII input if needed.

## Build Order (Stroke Ordering)

CJK characters have a canonical stroke order (the sequence in which you draw the strokes). Getting this right matters for pedagogy and for certain rendering techniques. CSDL handles stroke order through two mechanisms.

**Explicit ordering** uses the `build:` line to list stroke identifiers in drawing order. This is unambiguous.

**Implicit ordering** derives stroke order from the expression structure using recursive rules: top before bottom (in TB layouts), left before right (in LR layouts), outside before inside (in SUR layouts), and argument order for OVR and GRP.

There's one important subtlety: enclosure characters. In Chinese calligraphy, when a character has an outer enclosure (like the box in 國), you draw most of the outer strokes first, then the inner content, then the *closing stroke* of the enclosure (typically the bottom horizontal line). CSDL handles this with an optional `close:` marker in a component definition:

```
@comp 囗
build: s1 s2 s3
close: s3
s1 = S(shu [2,1] [2,11] 1)
s2 = S(heng-zhe [2,1] [10,1] [10,11] 1)
s3 = S(heng [2,11] [10,11] 1)
@end
```

When 囗 is used as the outer component of a `SUR` operator, the build order algorithm moves `s3` (the closing bottom stroke) to after the inner component's strokes. Without the `close:` marker, all outer strokes precede all inner strokes.

## Orthography Tags

The same Unicode code point can have different structural forms in different writing traditions. Traditional Chinese 國 (U+570B) has a different internal structure than Simplified Chinese 国 (U+56FD). Japanese Kanji underwent simplification reforms in 1946 and 1981, producing pre-reform and post-reform forms. Hong Kong and Taiwan have distinct standard glyph forms for some characters.

CSDL handles this with orthography tags drawn from the BCP 47 standard (the same tag system used for language identification on the web). The primary tags are `Hant` (Traditional Chinese), `Hans` (Simplified Chinese), `Jpan` (Japanese Kanji), `Kore` (Korean Hanja), and `Hani` (orthography-neutral Han). Extension tags using the `x-` prefix handle finer distinctions: `x-HantHK` and `x-HantTW` for Hong Kong versus Taiwan Traditional Chinese, `x-Kyuj` and `x-Shin` for pre-reform and post-reform Japanese, and tags for historically related scripts like Tangut, Khitan, and Vietnamese Chữ Nôm.

Orthography tags are pure metadata. They do not affect evaluation. A renderer targeting Japanese Kanji can use the tags to select the appropriate definition when multiple definitions exist for the same code point, but the geometric output of any given definition is identical regardless of its tag.

Tags can be set at three levels: file-wide (`@ortho Hant`), per-component, or per-character definition. More specific levels override less specific ones, so a predominantly Traditional Chinese file can include a few Simplified definitions without needing separate files.

A single file can contain multiple definitions for the same code point as long as they have distinct orthography tags:

```
U+570B guo2 = SUR(囗, 或) ortho:Hant rad:31 sc:11
U+56FD guo2 = SUR(囗, 玉) ortho:Hans rad:31 sc:8
```

Renderers select among competing definitions using the BCP 47 basic filtering algorithm against a tag hierarchy (e.g., `x-HantTW` falls back to `Hant`, which falls back to `Hani`).

## Conformance Levels

CSDL defines three conformance levels, each subsuming the previous:

**Level 1 (Parser)** must parse the grammar, validate all references, check acyclicity, enforce the closed operator sets, validate numeric bounds, and reject invalid input.

**Level 2 (Renderer)** must additionally resolve all references, compute bounding boxes, place children according to layout semantics, and emit positioned stroke geometry.

**Level 3 (Full)** must additionally expand strokes into filled outlines (closed paths suitable for rendering as filled regions).

Error handling strategy (stop at first error, collect all diagnostics, attempt partial output) is deliberately left implementation-defined. The spec only requires that invalid input is correctly rejected.

## Scope and Extensibility

CSDL targets roughly 98,000 CJK Unified Ideograph characters across all Unicode extension blocks. The stroke inventory is designed for Han-derived scripts, but the spec provides extension hooks for structurally adjacent scripts (Tangut, Khitan, Jurchen, Zhuang Sawndip, classical Yi) that share the stroke-based composition model. These scripts may need stroke primitives not in the current registry; authors working with them use the `x-` extension mechanism to flag non-standard stroke usage.

The extensibility model is deliberately conservative. New metadata fields and orthography tags are minor-version additions. New stroke names or operators require a major version bump because the closed-set enforcement means old parsers will reject files using new names. And the spec permanently forbids adding variables, conditionals, loops, macros, runtime stroke composition, or anything that would make evaluation non-terminating or non-deterministic. These are load-bearing design constraints, not aspirational goals.

## Security

Because CSDL is non-Turing and evaluation is bounded (output size is linear in input size), there is no mechanism by which a CSDL file can cause superlinear resource consumption. No executable code, no I/O, no network access. The attack surface is essentially zero. Implementations should handle the full ~98,000 character repertoire gracefully and may impose tighter limits for constrained environments.

## IDS Interoperability

CSDL maps cleanly to Unicode's Ideographic Description Sequence operators. The twelve IDS characters (⿰ through ⿻) map directly to CSDL layout operators: ⿰ → LR, ⿱ → TB, ⿲ → LR3, ⿳ → TB3, ⿴ → SUR(full), and so on for the various surround configurations and overlay. This enables mechanical translation from IDS to CSDL expressions. The reverse is lossy: CSDL's GRP, GRID, and some SUR side values have no IDS equivalents.

## What CSDL Makes Possible

CSDL fills a representation gap that has existed for decades. With a constructive grammar for character structure, several things become tractable that weren't before.

Font toolchains could accept CSDL input and generate outlines, preserving structural metadata through the compilation process. Educational software could present characters as build instructions rather than opaque images. Structural search becomes possible: find all characters that contain 木 on the left with a 4/8 split. Systematic comparison across orthographic traditions can be done programmatically rather than by manual inspection. Automated consistency checking can verify that a component used in hundreds of characters is defined identically everywhere. And machine learning systems working on character recognition or generation could use the structural decomposition as training signal rather than treating characters as undifferentiated pixel patterns.

The language is deliberately austere. Thirty-seven stroke types, eight layout operators, three transforms, a 12×12 grid. That's the entire vocabulary. The constraint is the point: by refusing to be a programming language, CSDL guarantees that every file is parseable, every expression terminates, and every implementation agrees on the output.

END
