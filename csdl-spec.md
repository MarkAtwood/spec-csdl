# CJK Stroke Description Language (CSDL) Specification

**Version:** 1.0
**Author:** Mark Atwood
**Date:** 2026-02-09  

---

## Abstract

CJK Stroke Description Language (CSDL) is a constructive,
non-Turing domain-specific language for describing the structural
composition of CJK ideographic characters from strokes, reusable
components, and spatial layout operators. CSDL fills the gap between
Unicode (which encodes identity, not structure), IDS (which is
symbolic, not geometric), font formats (which store flattened
outlines with no semantics), and pedagogical databases (which are
annotations, not grammars). CSDL produces deterministic geometric
descriptions of character structure from a closed set of primitives
and operators.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Conformance](#2-conformance)
3. [Terminology](#3-terminology)
4. [Data Model](#4-data-model)
5. [Coordinate System](#5-coordinate-system)
6. [Expression Grammar](#6-expression-grammar)
7. [Stroke Primitives](#7-stroke-primitives)
8. [Layout Operators](#8-layout-operators)
9. [Transform Operators](#9-transform-operators)
10. [Component Definitions](#10-component-definitions)
11. [Character Definitions](#11-character-definitions)
12. [Build Order Derivation](#12-build-order-derivation)
13. [Extensibility](#13-extensibility)
14. [Security Considerations](#14-security-considerations)
15. [References](#15-references)
16. [Appendix A: IDS Operator Mapping](#appendix-a-ids-operator-mapping)
17. [Appendix B: Kangxi Radical Registry (Representative)](#appendix-b-kangxi-radical-registry-representative)
18. [Appendix C: Compound Stroke Enumeration](#appendix-c-compound-stroke-enumeration)
19. [Appendix D: Complete Example File](#appendix-d-complete-example-file)
20. [Appendix E: Orthography Tag Registry](#appendix-e-orthography-tag-registry)

---

## 1. Introduction

### 1.1 Motivation

Existing standards and formats for CJK characters each address a
different concern and leave structural composition undescribed:

Unicode assigns code points to characters. It encodes identity
("this is U+660E ming2") but says nothing about how the character
is built from strokes or sub-components.

Ideographic Description Sequences (IDS, Unicode Annex) provide
symbolic decomposition using operators like ⿰ (left-right) and
⿱ (top-bottom), but these are purely topological. IDS does not
specify geometry, stroke coordinates, proportions, or rendering
parameters.

Font formats (OpenType, TrueType) store flattened cubic or
quadratic outlines. The stroke-level and component-level structure
is destroyed during font compilation. There is no way to recover
"this glyph is LR(日, 月)" from the outline data.

Pedagogical databases (CHISE, Unihan kDefinition, various stroke
order databases) annotate characters with structural metadata, but
these are informational annotations, not constructive grammars.
They cannot be evaluated to produce geometry.

CSDL occupies the missing layer: a constructive language that
takes stroke primitives, reusable named components, and spatial
layout operators as input, and produces deterministic geometric
descriptions of character structure as output.

### 1.2 Goals

The language is designed to satisfy the following goals:

**Constructive.** A CSDL expression can be evaluated to produce
stroke geometry. It is not an annotation; it is a build
specification.

**Deterministic.** The same input MUST always produce the same
output. There are no stochastic, context-dependent, or
implementation-defined evaluation behaviors.

**Non-Turing.** CSDL has no loops, variables, conditionals,
recursion, or macros. A character definition is a finite directed
acyclic graph (DAG) of nodes. Evaluation is a single pass: resolve
references, compute bounding boxes, place children, emit stroke
geometry. Evaluation always terminates.

**Terse.** Approximately 85% of characters can be described in a
single line. The remaining characters use multi-line block form for
complex component definitions.

**Composable.** Components are reusable. A component defined once
can be referenced by name in any number of character definitions.

**Closed.** All operator sets (strokes, layouts, transforms) are
enumerated and closed. An implementation MUST reject unknown
operators. This prevents dialect fragmentation and guarantees that
any conformant parser can process any conformant CSDL file.

### 1.3 Scope

CSDL describes the structural composition of characters in
stroke-based writing systems. Its primary targets are the CJK
ideographic scripts: Chinese (Traditional and Simplified),
Japanese Kanji, Korean Hanja, and Vietnamese Chữ Nôm. CSDL also
provides extensibility hooks for structurally adjacent scripts
that share the stroke-based composition model, such as Tangut,
Khitan (large script), Jurchen, Zhuang Sawndip, and classical Yi
(see Section 4.7 and Appendix E).

An optional orthography tag (`ortho:`) allows authors to annotate
definitions with their writing system or orthographic tradition
using IETF BCP 47 script subtags. Renderers MAY use orthography
tags for variant selection but MUST NOT require them for
evaluation.

CSDL does not address:

- Glyph rendering (anti-aliasing, hinting, rasterization)
- Font metrics (advance widths, kerning, vertical metrics)
- Text layout (line breaking, justification, bidi)
- Character encoding or identification (handled by Unicode)
- Stroke animation or temporal sequencing for pedagogy
- Aesthetic or calligraphic style variation

CSDL output is a tree of positioned strokes in a coordinate space.
A renderer MAY transform this output into filled outlines, SVG
paths, bitmap images, or any other representation. CSDL is
structural geometry, not rendering instructions; implementations
that require filled outlines, anti-aliasing, or rasterization
should transform CSDL output using standard graphics libraries.

### 1.4 Design Principles

**Principle 1: Enumerate, don't generate.** Compound strokes are
named primitives in a closed registry, not runtime compositions of
base strokes via a join operator. This eliminates an entire class
of combinatorial ambiguity.

**Principle 2: Layout is structural, not aesthetic.** Layout
operators describe spatial relationships (left-right, top-bottom,
surround). They do not encode calligraphic preferences. A renderer
MAY adjust proportions for aesthetic purposes; the CSDL expression
specifies the structural intent.

**Principle 3: Variants are named, not computed.** Positional
variants of components (e.g., 心.bot vs 心.left) are explicitly
named. Variant selection is a renderer RECOMMENDATION, not a
requirement. An author who cares about a specific variant SHOULD
use the variant name; an author who does not care MAY use the base
name and let the renderer choose.

**Principle 4: Ambiguity is the author's problem.** Cases like
radical 74/130 (月 moon vs 月 meat) are disambiguated by the
author using pinyin labels or explicit component references. CSDL
does not attempt automatic disambiguation.

---

## 2. Conformance

### 2.1 Key Words

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in
this document are to be interpreted as described in [BCP 14]
[RFC 2119] [RFC 8174] when, and only when, they appear in all
capitals, as shown here.

### 2.2 Conformance Levels

CSDL defines three conformance levels. Each level subsumes the
requirements of all lower levels.

**Level 1 (Parser).** A Level 1 conformant implementation MUST:

- Parse CSDL files according to the grammar in Section 6.
- Validate that all component references are resolvable.
- Validate that the component reference graph is acyclic.
- Validate that all operators are members of the closed sets
  defined in Sections 7, 8, and 9.
- Validate that all numeric parameters are within their
  specified bounds.
- Reject any input that violates the above constraints.

**Level 2 (Renderer).** A Level 2 conformant implementation MUST
additionally:

- Resolve all component references to their definitions.
- Compute bounding boxes for all nodes in the expression DAG.
- Place child nodes within parent bounding boxes according to
  layout operator semantics.
- Emit stroke geometry as positioned line segments with
  specified width values.

**Level 3 (Full).** A Level 3 conformant implementation MUST
additionally:

- Expand stroke geometry to filled outlines (closed paths suitable
  for rendering as filled regions).

### 2.3 Error Handling

Error recovery strategy (stop at first error, collect all
diagnostics, attempt partial output) is implementation-defined.
Error reporting format (human-readable messages, structured JSON,
error codes, line/column references) is implementation-defined.
This specification does not constrain error recovery or error
reporting behavior. A conformant implementation MUST correctly
reject invalid input; how it reports, formats, or recovers from
errors is a local decision.

### 2.4 Partial Conformance

An implementation that satisfies some but not all requirements of a
conformance level MUST NOT claim conformance to that level. An
implementation MAY claim conformance to a lower level while noting
specific additional capabilities from higher levels.

---

## 3. Terminology

**base stroke**
: One of the 11 fundamental stroke types from which all CJK
  strokes are composed. See Section 7.1.

**bounding box**
: A rectangular region in the coordinate system defined by its
  top-left corner and bottom-right corner. Every node in a CSDL
  expression has a bounding box.

**character definition**
: A CSDL expression that describes a complete CJK character by
  its Unicode code point, an optional pinyin name, and a
  structural expression.

**component**
: A named, reusable sub-structure that can be referenced by name
  in character definitions and other component definitions.
  Components are defined in block form.

**compound stroke**
: One of the 26 named multi-segment stroke types. Each compound
  stroke is a single named primitive in the closed stroke registry.
  See Section 7.2.

**DAG**
: Directed Acyclic Graph. The reference structure of a CSDL
  expression, where nodes are components or strokes and edges are
  references from parent to child.

**expression**
: A CSDL construct that evaluates to stroke geometry within a
  bounding box. Expressions are either stroke invocations, layout
  operator applications, transform operator applications, or
  component references.

**grid unit**
: The fundamental unit of the CSDL coordinate system. One grid
  unit equals 1/12th of the containing bounding box dimension.

**inline form**
: A character definition expressed as a single line of CSDL.

**block form**
: A component or character definition expressed as multiple lines
  delimited by `@comp`/`@end` or `@char`/`@end` markers.

**layout operator**
: One of the 8 spatial composition operators (LR, TB, LR3, TB3,
  SUR, OVR, GRP, GRID) that arrange child expressions within a
  bounding box. See Section 8.

**positional variant**
: A named variant of a component that specifies its rendering
  when placed in a particular structural position (e.g., 心.bot
  for 心 when used as a bottom component). Expressed using dotted
  name syntax. Variant tags are open-ended lowercase ASCII
  identifiers; common tags include `left`, `right`, `top`, `bot`,
  `inner`, `outer`, `simp`, `alt`, and compound forms like
  `left.simp`. A component name MAY carry multiple chained tags.

**split**
: A numeric parameter to layout operators that specifies how the
  parent bounding box is divided among children. The renderer
  divides the parent box proportionally according to the split
  values.

**stroke**
: A geometric primitive consisting of one or more connected line
  segments with a specified width. Strokes are the leaf nodes of
  CSDL expression trees.

**transform operator**
: One of the 3 geometric modification operators (sc, sh, sk) that
  alter the scale, position, or skew of a child expression. See
  Section 9.

**orthography tag**
: A BCP 47 script subtag (or registered CSDL extension tag)
  indicating the writing system or orthographic tradition that a
  component or character definition belongs to. Orthography tags
  are metadata; they MUST NOT affect evaluation but renderers MAY
  use them for variant selection. See Section 4.7.

---

## 4. Data Model

### 4.1 Overview

A CSDL file is a UTF-8 encoded, line-oriented text file containing
a sequence of definitions. Definitions are of four kinds:

1. **Alias definitions** bind an ASCII pinyin name to a Unicode
   component name.
2. **Component definitions** define named, reusable sub-structures
   in block form.
3. **Character definitions** define complete characters, either in
   inline form (one line) or block form (multiple lines).
4. **Comments** are lines beginning with `#`.

### 4.2 File Structure

A CSDL file MUST be encoded as UTF-8 [RFC 3629] without BOM. Line
endings MUST be LF (U+000A) or CR LF (U+000D U+000A); a
conformant parser MUST accept both.

Horizontal whitespace (U+0020 SPACE and U+0009 TAB) is
interchangeable wherever the grammar permits `WS`. Leading and
trailing whitespace on any line is not significant.

All Unicode text in a CSDL file SHOULD be in NFC [UAX #15].
Component name matching operates on the raw code point sequence;
a conformant parser MUST NOT apply normalization during name
resolution. A parser MAY reject a file containing non-NFC text.

The conventional file extension for CSDL files is `.csdl`. The
proposed media type is `text/csdl` (see Section 15.2).

A CSDL file MUST begin with a format declaration as its first
non-comment, non-blank line:

    @csdl 1.0

A Level 1 parser MUST reject files without a `@csdl` declaration.
A parser that encounters a `@csdl` declaration with a major
version it does not support MUST reject the file. A parser that
encounters a `@csdl` declaration with a recognized major version
but an unknown minor version SHOULD issue a warning and continue
processing.

Blank lines and comment lines MAY appear anywhere in the file.
Comment lines begin with `#` as the first non-whitespace character.

### 4.2.1 Version Compatibility Contract

A minor version increment (e.g., 1.0 to 1.1) indicates additions
that do not alter the meaning of existing constructs. Specifically,
a minor version MAY add new metadata fields, new orthography tags,
and new entries to Appendix E. A minor version MUST NOT add new
stroke names, layout operators, or transform operators.

A major version increment (e.g., 1.x to 2.0) is required for any
change that would cause a conformant v1 parser to reject a
previously valid file, or that alters the evaluated geometry of an
existing construct. Adding a new stroke name or operator to the
closed registries is a major version change, because a v1 parser
enforcing the closed set will reject files that use the new name.

A Level 1 parser conformant to version N.x MUST accept any file
declared as version N.y where y >= x, ignoring unknown metadata
fields and unknown orthography tags. It MUST reject files declared
as version M.z where M > N.

Definitions MAY appear in any order, with the constraint that
circular references are forbidden (Section 4.4). However, authors
SHOULD place alias definitions before their first use, and
component definitions before character definitions that reference
them, for readability.

### 4.2.2 Multi-File Composition

CSDL does not define an import, include, or file-reference
mechanism. Each CSDL file is a self-contained unit for parsing
purposes; all component names referenced in a file MUST be
defined or aliased within that same file.

In practice, toolchains will maintain shared component libraries
(e.g., a base file containing the Kangxi 214 radical definitions)
and concatenate or merge them with character definition files before
parsing. This concatenation is a tooling concern and is outside the
scope of this specification. However, to ensure interoperability,
toolchains performing concatenation SHOULD apply the following
rules:

- **`@csdl` declaration:** The first `@csdl` declaration in
  concatenation order wins. Subsequent `@csdl` declarations
  SHOULD be stripped or treated as an error.
- **`@ortho` declaration:** The first `@ortho` declaration in
  concatenation order wins. Subsequent `@ortho` declarations
  SHOULD be stripped or treated as an error.
- **Duplicate component names:** Last definition wins, per §4.5.
- **Duplicate alias names:** Error, per constraint 25.
- **Duplicate character definitions:** Error if same code point
  with same `ortho:` tag, per §4.7.5.

The concatenated result MUST be a valid CSDL file.

### 4.3 Expression DAG

Every character definition evaluates to a finite DAG. The nodes of
the DAG are:

- **Stroke nodes** (leaves): invoke a named stroke primitive with
  coordinate and width parameters.
- **Layout nodes** (internal): apply a layout operator to 2-8
  child expressions.
- **Transform nodes** (internal): apply a transform operator to
  exactly 1 child expression.
- **Reference nodes** (internal, resolved): reference a named
  component, which is itself a DAG.

After reference resolution, the complete structure is a tree (since
each reference is expanded to its own copy of the referenced
sub-DAG for evaluation purposes). The DAG structure exists at the
definition level; the evaluated structure is a tree.

### 4.4 Acyclicity Constraint

The component reference graph MUST be acyclic. That is, no
component definition MAY reference itself, directly or indirectly.
A Level 1 conformant implementation MUST detect and reject cycles.

Formally: let G = (V, E) where V is the set of all defined
components and E contains an edge (a, b) if component a references
component b. G MUST be a DAG.

### 4.5 Duplicate Component Definitions

A CSDL file MAY contain multiple `@comp` blocks with the same
component name. When duplicates exist, the last definition in file
order wins. A conformant parser MAY issue a warning on duplicate
component names but MUST NOT reject the file.

### 4.6 Metadata

Character definitions MAY include metadata fields. Metadata is
informational and MUST NOT affect evaluation. The following
metadata fields are defined:

- `rad:` Kangxi radical number (integer 1-214)
- `sc:` Total stroke count (positive integer)
- `freq:` Frequency rank (positive integer)
- `ortho:` Orthography tag(s) (see Section 4.7)

Additional metadata fields MAY be defined by implementations but
MUST be prefixed with `x-` to avoid collision with future standard
fields.

### 4.7 Orthography Tags

CSDL defines an optional orthography tag (`ortho:`) that indicates
the writing system or orthographic tradition a definition belongs
to. Orthography tags enable a single CSDL file to contain
definitions for multiple script traditions (e.g., both Traditional
and Simplified Chinese forms of the same character) and allow
renderers to filter or select definitions appropriate to a target
orthography.

#### 4.7.1 Tag Format

An orthography tag value MUST be one of:

1. A registered BCP 47 script subtag (e.g., `Hant`, `Hans`,
   `Jpan`, `Kore`). See Appendix E for the complete registry.
2. A CSDL extension tag prefixed with `x-` for scripts not yet
   covered by BCP 47 or the CSDL registry (e.g., `x-Tang`,
   `x-Khit`).

Tags are case-sensitive. Authors MUST use the canonical casing
defined in Appendix E.

#### 4.7.2 Semantics

Orthography tags are metadata. They MUST NOT affect evaluation.
A CSDL expression produces identical geometric output regardless
of the presence or value of an `ortho:` tag.

Renderers MAY use orthography tags for the following purposes:

- **Variant selection.** When multiple definitions exist for the
  same code point with different `ortho:` tags, a renderer MAY
  select the definition matching a target orthography.
- **Filtering.** A renderer MAY ignore definitions whose `ortho:`
  tag does not match the rendering context.
- **Stroke count validation.** Different orthographies may assign
  different standard stroke counts to the same character; the
  `ortho:` tag provides context for the `sc:` metadata.

Renderers MUST NOT reject definitions that lack an `ortho:` tag.
A definition without an `ortho:` tag is orthography-neutral and
is valid in any context.

Fallback behavior when no definition matches the requested
orthography is implementation-defined. A renderer MAY return an
untagged definition, return an error, skip the character, or apply
other fallback strategies.

#### 4.7.3 Scope Levels

Orthography tags may be applied at three levels of granularity:

**File level.** A file-level orthography declaration applies to
all definitions in the file unless overridden:

    @ortho Hant

**Component level.** An `ortho:` metadata field on a `@comp`
block applies to that component:

    @comp 門
    build: s1 s2 ...
    ...
    ortho: Hant
    @end

**Character level.** An `ortho:` metadata field on a character
definition (inline or block) applies to that character:

    U+660E ming2 = LR(日, 月) ortho:Hant rad:72 sc:8

More specific levels override less specific levels. A character-
level `ortho:` tag overrides a file-level `@ortho` declaration.
A component-level `ortho:` tag overrides a file-level `@ortho`
declaration. This allows a predominantly Traditional Chinese file
to include a few Simplified definitions without separate files.

#### 4.7.4 Multiple Orthographies

A single definition MAY carry multiple orthography tags,
separated by commas:

    U+660E ming2 = LR(日, 月) ortho:Hant,Jpan rad:72 sc:8

This indicates the definition is valid for both Traditional
Chinese and Japanese contexts. Renderers MAY match on any tag in
the list.

#### 4.7.5 Multiple Definitions per Code Point

A CSDL file MAY contain multiple definitions for the same Unicode
code point, provided they have distinct `ortho:` tags:

    U+570B guo2 = SUR(囗, 或) ortho:Hant rad:31 sc:11
    U+56FD guo2 = SUR(囗, 玉) ortho:Hans rad:31 sc:8

A Level 1 parser MUST reject multiple definitions for the same
code point with the same `ortho:` tag (or both lacking an
`ortho:` tag). Multiple definitions with distinct tags, or one
tagged and one untagged, are permitted.

### 4.8 File-Level Declarations

A CSDL file MAY contain a file-level orthography declaration:

    @ortho TAG

This declaration MUST appear before any definition in the file
(aliases, components, or characters). Only one `@ortho`
declaration is permitted per file. It sets the default orthography
for all definitions in the file that do not carry their own
`ortho:` tag.

---

## 5. Coordinate System

### 5.1 Grid

The CSDL coordinate system divides the bounding box into a 12x12
grid of integer coordinates.

- The origin `[0,0]` is at the top-left corner.
- The X axis increases to the right.
- The Y axis increases downward.
- `[12,12]` is the bottom-right corner.
- `[6,6]` is the center.

The value 12 is chosen because it is divisible by 2, 3, 4, and 6.
This means halves (6), thirds (4), quarters (3), and sixths (2)
all land on integer coordinates, eliminating rounding for the most
common subdivisions.

### 5.2 Child Box Inheritance

When a layout operator divides a parent bounding box into child
regions, each child region becomes a new `[0,0]`-`[12,12]`
coordinate space. Stroke coordinates within a child expression are
relative to the child's own bounding box, not the parent's.

### 5.3 /24 Override

For components that require finer positioning than the 12-unit grid
provides, a coordinate MAY be specified in 24ths by appending `/24`
to the value. In /24 mode, the bounding box spans `[0,0]` to
`[24,24]`.

The /24 override applies to a single `@comp` block. It is declared
on the `@comp` line:

    @comp 辶.bot /24
    ...
    @end

Within a /24 block, all stroke coordinates use the 24-unit grid.
Layout operators and transform operators are unaffected; they
continue to use 12-unit splits.

The default grid for all `@comp` and `@char` blocks is `/12`
(the standard 12-unit grid defined in Section 5.1). The `/12`
specifier is implicit and SHOULD NOT appear in a CSDL file. A
parser encountering `/12` SHOULD treat it as equivalent to the
default and MAY issue a warning.

### 5.4 Stroke Width

Stroke width is specified as an integer value:

- `0` = hairline
- `1` = normal weight
- `2` = bold weight

Implementations MAY map these values to pixel widths, em-relative
widths, or other concrete measures as appropriate for the output
format.

---

## 6. Expression Grammar

This section defines the complete formal grammar of CSDL using
W3C-style EBNF notation. All productions are finite; there is no
recursion except through named component references, which are
constrained to be acyclic (Section 4.4).

### 6.1 Notation

The grammar uses W3C EBNF notation as defined in the XML
specification [W3C XML], Section 6, with the following
conventions:

- `'literal'` denotes a terminal string.
- `#xN` denotes a Unicode code point.
- `/* ... */` and `(* ... *)` are grammar comments (not part of
  the language).

In addition to standard W3C EBNF, this grammar uses POSIX-style
character class notation for readability: `[a-z]` denotes any
Unicode scalar value from U+0061 to U+007A inclusive; `[0-9]`
denotes U+0030 to U+0039; `[a-zA-Z]` denotes the union of
`[a-z]` and `[A-Z]` (U+0041 to U+005A and U+0061 to U+007A);
`[1-4]` denotes U+0031 to U+0034. The negation syntax
`[^#xN#xM]` denotes any scalar value except those listed.

### 6.2 Lexical Productions

```ebnf
(* Whitespace and line structure *)
WS          ::= ( #x20 | #x09 )+
NL          ::= #x0A | ( #x0D #x0A )
BLANK_LINE  ::= WS? NL
COMMENT     ::= WS? '#' [^#x0A#x0D]* NL

(* Basic tokens *)
DIGIT       ::= [0-9]
LETTER      ::= [a-zA-Z]
INT         ::= '-'? DIGIT+
UINT        ::= DIGIT+
TONE        ::= [1-5]   (* 5 = neutral tone / 轻声 *)

(* Unicode code point label: U+ followed by 4 or 6 hex digits *)
CODEPOINT   ::= 'U+' [0-9A-Fa-f] [0-9A-Fa-f] [0-9A-Fa-f] [0-9A-Fa-f]
                ( [0-9A-Fa-f] [0-9A-Fa-f] )?

(* CJK character: any scalar value assigned to a block whose name
   begins with "CJK Unified Ideographs" or "CJK Compatibility
   Ideographs" as defined by the version of the Unicode Standard
   referenced in §15.1.

   Informative note: the following ranges reflect Unicode 16.0.
   Implementations MUST accept code points from later extensions
   that satisfy the normative definition above. *)
CJK_CHAR    ::= [#x3400-#x9FFF]
              | [#xF900-#xFAFF]
              | [#x20000-#x2FA1F]
              | [#x30000-#x3134F]
              | [#x31350-#x323AF]

(* Pinyin syllable: lowercase letters followed by tone number *)
PINYIN_SYLL ::= [a-z]+ TONE

(* Component names *)
PINYIN_NAME ::= PINYIN_SYLL ( PINYIN_SYLL )*
VARIANT_TAG ::= '.' [a-z] [a-z0-9]*
COMP_NAME   ::= ( CJK_CHAR | PINYIN_NAME ) ( VARIANT_TAG )*
```

### 6.3 Coordinate Productions

```ebnf
(* Coordinate pair: [x,y] *)
COORD       ::= '[' UINT ',' UINT ']'

(* Grid override *)
GRID_SPEC   ::= '/24' | '/12'

(* Stroke width *)
WIDTH       ::= '0' | '1' | '2'
```

### 6.4 Stroke Productions

```ebnf
(* Standard stroke name: a lowercase ASCII identifier with optional
   hyphen separators. All STD_STROKE values MUST be members of the
   closed stroke registry defined in §7 and Appendix C. A Level 1
   parser MUST reject any standard stroke name not in the registry. *)
STD_STROKE  ::= [a-z]+ ( '-' [a-z]+ )*

(* Extension stroke name: x- prefix followed by lowercase ASCII with
   optional hyphens. Extension strokes are experimental or non-standard.
   A Level 1 parser MUST accept x- prefixed stroke names without
   validating against the closed registry. Renderer behavior for
   extension strokes is implementation-defined. *)
EXT_STROKE  ::= 'x-' [a-z]+ ( '-' [a-z]+ )*

STROKE_NAME ::= STD_STROKE | EXT_STROKE

(* Stroke invocation *)
STROKE_EXPR ::= 'S(' STROKE_NAME WS COORD ( WS COORD )+ WS WIDTH ')'
```

### 6.5 Layout Operator Productions

```ebnf
(* Split specification: comma-separated positive integers.
   Split values are proportional; the renderer divides the parent
   box according to the ratio of the values. Values summing to 12
   align with grid boundaries but this is not required.
   No whitespace is permitted around the '/' separator. *)
SPLIT_2     ::= UINT '/' UINT
SPLIT_3     ::= UINT '/' UINT '/' UINT

(* Surround side *)
SUR_SIDE    ::= 'full' | 'tl' | 'tr' | 'top' | 'right' | 'left'
              | 'bot' | 'bl' | 'br'

(* Inset value: integer 0-6 *)
INSET       ::= UINT

(* Layout operators *)
LR_EXPR     ::= 'LR(' EXPR ',' WS? EXPR ( ',' WS? SPLIT_2 )? ')'
TB_EXPR     ::= 'TB(' EXPR ',' WS? EXPR ( ',' WS? SPLIT_2 )? ')'
LR3_EXPR    ::= 'LR3(' EXPR ',' WS? EXPR ',' WS? EXPR
                  ( ',' WS? SPLIT_3 )? ')'
TB3_EXPR    ::= 'TB3(' EXPR ',' WS? EXPR ',' WS? EXPR
                  ( ',' WS? SPLIT_3 )? ')'
SUR_EXPR    ::= 'SUR(' EXPR ',' WS? EXPR
                  ( ',' WS? SUR_SIDE ( ',' WS? INSET )? )? ')'
OVR_EXPR    ::= 'OVR(' EXPR ',' WS? EXPR ')'
GRP_EXPR    ::= 'GRP(' EXPR ( ',' WS? EXPR )+ ')'
GRID_EXPR   ::= 'GRID(' EXPR ',' WS? EXPR ',' WS? EXPR ',' WS? EXPR
                  ( ',' WS? SPLIT_2 ',' WS? SPLIT_2 )? ')'

LAYOUT_EXPR ::= LR_EXPR | TB_EXPR | LR3_EXPR | TB3_EXPR
              | SUR_EXPR | OVR_EXPR | GRP_EXPR | GRID_EXPR
```

Note on parsing ambiguity: the optional split parameter in `LR`,
`TB`, `LR3`, and `TB3` expressions appears in a position where an
`EXPR` argument could also occur. There is no ambiguity because a
split value (e.g., `4/8`) always begins with `DIGIT '/'`, which is
not a valid start for any `EXPR` production. Parsers MAY use this
single-token lookahead to distinguish splits from expressions.

### 6.6 Transform Operator Productions

```ebnf
(* Transform parameter: bounded integer -12 to 24.
   24 = 2× the grid dimension, sufficient for all known composition
   patterns; exceeding this range suggests a modeling error. *)
TPARAM      ::= INT   /* constrained: -12 <= value <= 24 */

(* Transform operators *)
SC_EXPR     ::= 'sc(' EXPR ',' WS? 'sx=' TPARAM ',' WS? 'sy=' TPARAM ')'
SH_EXPR     ::= 'sh(' EXPR ',' WS? 'dx=' TPARAM ',' WS? 'dy=' TPARAM ')'
SK_EXPR     ::= 'sk(' EXPR ',' WS? 'kx=' TPARAM ',' WS? 'ky=' TPARAM ')'

XFORM_EXPR  ::= SC_EXPR | SH_EXPR | SK_EXPR
```

### 6.7 Expression Production

```ebnf
(* An expression is a stroke, layout, transform, or component ref *)
EXPR        ::= STROKE_EXPR
              | LAYOUT_EXPR
              | XFORM_EXPR
              | COMP_NAME
```

### 6.8 Definition Productions

```ebnf
(* Alias definition *)
ALIAS_DEF   ::= '@alias' WS COMP_NAME WS '=' WS CJK_CHAR NL

(* Metadata fields *)
META_RAD    ::= 'rad:' WS? UINT
META_SC     ::= 'sc:' WS? UINT
META_FREQ   ::= 'freq:' WS? UINT
META_ORTHO  ::= 'ortho:' WS? ORTHO_LIST
META_EXT    ::= 'x-' LETTER+ ':' WS? [^#x0A#x0D]+ 
METADATA    ::= META_RAD | META_SC | META_FREQ | META_ORTHO | META_EXT

(* Orthography tags.
   An ORTHO_TAG that is not a CSDL extension tag (i.e., does not
   begin with 'x-') MUST be a valid ISO 15924 script subtag as
   registered in the IANA Language Subtag Registry [BCP 47].
   Informative note: all ISO 15924 script subtags are currently
   4 ASCII letters. *)
BCP47_TAG   ::= LETTER LETTER LETTER LETTER   /* ISO 15924 script subtag */
CSDL_XTAG   ::= 'x-' LETTER+
ORTHO_TAG   ::= BCP47_TAG | CSDL_XTAG
ORTHO_LIST  ::= ORTHO_TAG ( ',' ORTHO_TAG )*

(* Format declaration *)
FORMAT_DECL  ::= '@csdl' WS DIGIT+ '.' DIGIT+ NL

(* File-level orthography declaration *)
ORTHO_DECL  ::= '@ortho' WS ORTHO_TAG NL

(* Build order: explicit stroke ordering or expression delegation *)
BUILD_STROKES ::= 'build:' WS? STROKE_ID ( WS STROKE_ID )*
BUILD_EXPR    ::= 'build:' WS? 'from_expr'
BUILD_LINE    ::= BUILD_STROKES | BUILD_EXPR
STROKE_ID     ::= [a-z] [a-z0-9]*

(* Closing stroke marker *)
CLOSE_LINE    ::= 'close:' WS? STROKE_ID

(* Stroke definition line within a @comp block *)
STROKE_DEF  ::= STROKE_ID WS '=' WS STROKE_EXPR

(* Component body: either stroke definitions or a single expression *)
COMP_STROKE_BODY ::= ( BUILD_STROKES NL )?
                     ( CLOSE_LINE NL )?
                     ( STROKE_DEF NL )+
COMP_EXPR_BODY   ::= BUILD_EXPR NL
                     EXPR NL

(* Component block form *)
COMP_BLOCK  ::= '@comp' WS COMP_NAME ( WS GRID_SPEC )? NL
                ( COMP_STROKE_BODY | COMP_EXPR_BODY )
                ( METADATA NL )*
                '@end' NL

(* Character inline form *)
CHAR_INLINE ::= ( CODEPOINT | CJK_CHAR ) WS PINYIN_NAME WS '=' WS EXPR
                ( WS METADATA )* NL

(* Character block form *)
CHAR_STROKE_BODY ::= ( BUILD_STROKES NL )?
                     ( CLOSE_LINE NL )?
                     ( STROKE_DEF NL )+
CHAR_EXPR_BODY   ::= BUILD_EXPR NL
                     EXPR NL

CHAR_BLOCK  ::= '@char' WS ( CODEPOINT | CJK_CHAR ) WS PINYIN_NAME NL
                ( CHAR_STROKE_BODY | CHAR_EXPR_BODY )
                ( METADATA NL )*
                '@end' NL

(* Top-level definitions *)

(* Semantic note: when a CHAR_INLINE or CHAR_BLOCK uses a CJK_CHAR
   rather than a CODEPOINT as its leading token, the code point
   identity of the character definition is the Unicode scalar value
   of that CJK_CHAR. For example, 明 ming2 = LR(日, 月) is
   equivalent to U+660E ming2 = LR(日, 月). *)

DEFINITION  ::= ALIAS_DEF | COMP_BLOCK | CHAR_INLINE | CHAR_BLOCK

(* File *)
CSDL_FILE   ::= FORMAT_DECL
                ORTHO_DECL?
                ( DEFINITION | COMMENT | BLANK_LINE )*
```

### 6.9 Semantic Constraints

The following constraints are not expressible in the EBNF grammar
and MUST be enforced by a conformant Level 1 parser. This section
is the single canonical location for all semantic constraints on
CSDL syntax. Where earlier sections restate these constraints in
prose, the wording here governs in case of any inconsistency.

1. All `SPLIT_2` values MUST be positive integers. Values summing
   to 12 SHOULD be preferred because they align with grid unit
   boundaries. (See §8.2.)
2. All `SPLIT_3` values MUST be positive integers. Values summing
   to 12 SHOULD be preferred. (See §8.4.)
3. All `TPARAM` values MUST be in the range -12 to 24 inclusive.
   Rationale: 24 equals 2× the grid dimension, which is sufficient
   for all known composition patterns; values exceeding this range
   suggest a modeling error. (See §9.1.)
4. All `INSET` values MUST be in the range 0 to 6 inclusive.
   (See §8.6.)
5. All `WIDTH` values MUST be 0, 1, or 2. (See §5.4.)
6. All coordinate values in `COORD` within a standard block MUST
   be in the range 0 to 12 inclusive. (See §5.1.)
7. All coordinate values in `COORD` within a `/24` block MUST be
   in the range 0 to 24 inclusive. (See §5.3.)
8. The `GRP` operator MUST have at least 2 child expressions.
   (See §8.8.)
9. All `COMP_NAME` references MUST resolve to a defined component
   or alias. (See §4.3.)
10. The component reference graph MUST be acyclic. (See §4.4.)
11. All `STROKE_NAME` values MUST be members of the closed stroke
    registry defined in §7 and Appendix C.
12. All stroke invocations MUST provide the correct number of
    coordinate points for the named stroke. (See §7.3.)
13. A `COMP_BLOCK` with `build: from_expr` MUST contain exactly
    one `EXPR` line and zero `STROKE_DEF` lines. (See §10.3.)
14. A `COMP_BLOCK` with stroke definitions MUST contain one or more
    `STROKE_DEF` lines and MUST NOT contain bare `EXPR` lines.
    (See §10.1.)
15. A `COMP_BLOCK` MUST NOT specify both `/24` and
    `build: from_expr`. (See §10.4.)
16. All `ORTHO_TAG` values MUST be either a valid ISO 15924 script
    subtag as registered in the IANA Language Subtag Registry
    [BCP 47] and listed in Appendix E, or a CSDL extension tag
    matching `x-` followed by one or more ASCII letters.
    (See §4.7.1.)
17. A CSDL file MUST NOT contain more than one `@ortho`
    declaration. (See §4.8.)
18. The `@ortho` declaration, if present, MUST appear before any
    `DEFINITION` in the file (comments and blank lines excepted).
    (See §4.8.)
19. The `@csdl` declaration, if present, MUST appear before the
    `@ortho` declaration and before any `DEFINITION` in the file
    (comments and blank lines excepted). (See §4.2.)
20. A CSDL file MUST NOT contain multiple definitions for the same
    `CODEPOINT` with the same `ortho:` tag value (or both lacking
    an `ortho:` tag). (See §4.7.5.)
21. A `CHAR_BLOCK` with `build: from_expr` MUST contain exactly
    one `EXPR` line and zero `STROKE_DEF` lines. (See §11.2.)
22. A `CHAR_BLOCK` with stroke definitions MUST contain one or
    more `STROKE_DEF` lines and MUST NOT contain bare `EXPR`
    lines. (See §11.2.)
23. In a `@comp` or `@char` block with an explicit `build:`
    line, the set of stroke identifiers in the `build:` line
    MUST equal the set of stroke identifiers defined in the
    block, with no omissions and no extras. (See §12.1.)
24. The set of alias names and the set of component names
    defined in a CSDL file MUST be disjoint. No name MAY
    appear as both an alias target and a component name.
    (See §10.7.)
25. Each alias name MUST be defined at most once. A CSDL file
    MUST NOT contain multiple `@alias` definitions with the
    same left-hand side name. (See §10.7.)
26. If a `close:` line is present in a `@comp` or `@char` block,
    the stroke identifier it names MUST appear in the `build:`
    line (if explicit) or among the stroke definitions in the
    block. A `close:` line MUST NOT appear in an expression-form
    block (`build: from_expr`). (See §12.4.)
27. A `GRID` expression with split parameters MUST provide both
    `hsplit` and `vsplit`. Providing only one is a parse error.
    (See §8.9.)

---

## 7. Stroke Primitives

### 7.1 Base Strokes

CSDL defines 11 base stroke types. These are the atomic geometric
primitives from which all CJK strokes are built. Each base stroke
has a standard name, a minimum point count, and a geometric
interpretation.

| Name   | Pinyin  | Min Points | Geometry                     |
|--------|---------|------------|------------------------------|
| heng   | heng2   | 2          | Horizontal, left to right    |
| shu    | shu4    | 2          | Vertical, top to bottom      |
| pie    | pie3    | 2          | Left-falling diagonal        |
| na     | na4     | 2          | Right-falling diagonal       |
| dian   | dian3   | 2          | Dot (short stroke)           |
| ti     | ti2     | 2          | Rising stroke, lower-left to upper-right |
| gou    | gou1    | 2          | Hook (terminal turn)         |
| wan    | wan1    | 2          | Bend (smooth curve)          |
| zhe    | zhe2    | 2          | Sharp turn                   |
| xie    | xie2    | 2          | Slant                        |
| wo     | wo4     | 2          | Reclining hook               |

Note on `dian`: Like all strokes, `dian` is defined by two
coordinate points specifying a start and end. The vector from
start to end defines the dot's direction and extent. A renderer
determines the visual shape of the dot (e.g., rounded, teardrop,
or triangular) based on the stroke direction and the target
calligraphic style.

Note on curved strokes: For strokes with curved geometry (`wan`,
`gou`, `wo`, and compounds containing them), the coordinate points
define the path the stroke passes through. The interpolation
method between points (e.g., straight segments, quadratic Bézier,
Catmull-Rom spline) is renderer-discretionary. Two conformant
renderers MAY produce visually different curves from identical
coordinates.

### 7.2 Compound Strokes

CSDL defines 26 compound stroke types. Each compound stroke is a
named primitive in a closed registry. Compound strokes are NOT
composed at runtime from base strokes; they are atomic named
types.

The compound stroke name encodes the sequence of stroke segments
joined at fold points. For example, `heng-zhe` is a horizontal
segment followed by a sharp turn into a vertical segment. The
"fold count" of a compound stroke is the number of direction
changes (joints between segments), which is one less than the
segment count. A "single-fold" compound has 2 segments and 1
joint; a "double-fold" has 3 segments and 2 joints; and so on.

The full enumeration is given in Appendix C.

### 7.3 Point Count Rule

Each stroke type has a minimum number of coordinate points. The
minimum point count for a compound stroke is computed from its
constituent segments:

    total_points = sum(min_points_per_segment) - (N - 1)

where N is the number of segments. This is because adjacent
segments share their junction point.

For all base strokes, `min_points = 2`. Therefore, for a compound
stroke with N segments:

    total_points = 2N - (N - 1) = N + 1

Examples:

- `heng` (1 segment): 2 points
- `heng-zhe` (2 segments): 3 points
- `heng-zhe-zhe` (3 segments): 4 points
- `heng-zhe-zhe-zhe` (4 segments): 5 points
- `heng-zhe-zhe-zhe-gou` (5 segments): 6 points

### 7.4 Stroke Invocation Syntax

A stroke is invoked using the `S()` function:

    S(stroke_name [x1,y1] [x2,y2] ... [xN,yN] width)

The number of coordinate pairs MUST equal the minimum point count
for the named stroke type. A Level 1 parser MUST reject a stroke
invocation whose coordinate count does not match the minimum point
count for the named stroke.

Example:

    S(heng [2,4] [10,4] 1)

This invokes a `heng` (horizontal) stroke from point [2,4] to
point [10,4] with normal width (1).

    S(heng-zhe [3,2] [9,2] [9,10] 1)

This invokes a `heng-zhe` (horizontal-turn) stroke through three
points with normal width.

The coordinate points of a stroke invocation define the drawing
direction of the stroke. The first point is the starting point;
the last point is the ending point. Pen motion proceeds through
the points in the order given.

For compound strokes, the coordinate points are junction points
(the points where the pen changes direction). A conformant parser
treats compound stroke coordinates as connect-the-dots geometry:
the named segments are drawn between consecutive points in order,
but no geometric constraint is enforced on the angles or
directions implied by the compound stroke name. The name serves
as a semantic label (identifying the stroke type for stroke-count
purposes and pedagogical classification), not as a geometric
constraint on the coordinate values. Two renderers given the
same coordinates MUST produce the same line segments regardless
of whether those segments "look like" the named stroke type.

A conformant parser MUST NOT reject a stroke invocation solely
because its coordinate values produce geometry inconsistent with
the stroke name's conventional direction. However, a parser MAY
emit a warning when stroke coordinate geometry appears inconsistent
with the stroke name (e.g., a stroke labeled `heng` with vertical
coordinates). Such warnings are advisory and do not affect
conformance.

### 7.5 Extension Strokes

For scripts not fully covered by the 37-stroke registry (e.g.,
Tangut, Khitan, or experimental notations), CSDL permits extension
stroke names prefixed with `x-`. Examples: `x-tangut-loop`,
`x-khitan-dot`, `x-experimental-curve`.

A Level 1 parser MUST accept `x-` prefixed stroke names without
validating them against the closed registry. The coordinate count
for extension strokes is not specified; parsers SHOULD accept any
count >= 2.

Renderer behavior for extension strokes is implementation-defined.
A renderer MAY render extension strokes as their coordinate
segments (fallback), MAY ignore them, or MAY implement custom
handling for recognized extension names.

Extension strokes are intended for experimentation and specialized
use cases. Widely-adopted extensions may be promoted to the
standard registry in a future major version.

---

## 8. Layout Operators

### 8.1 Overview

CSDL defines 8 layout operators that arrange child expressions
within a parent bounding box. Layout operators divide the parent
box into child regions and assign each child expression to a
region.

### 8.2 LR (Left-Right)

    LR(a, b)
    LR(a, b, split)

Divides the parent box into two regions side by side. Child `a`
occupies the left region, child `b` the right. The default split
is 6/6 (equal halves). The split parameter specifies the number
of grid units allocated to each child. Split values are
proportional; the renderer divides the parent box according to
the ratio of the values. Values summing to 12 align with grid
unit boundaries and SHOULD be preferred.

Example: `LR(日, 月)` places 日 on the left and 月 on the right.

Example: `LR(亻, 寺, 4/8)` allocates 4 units to 亻 and 8 to 寺.

### 8.3 TB (Top-Bottom)

    TB(a, b)
    TB(a, b, split)

Divides the parent box into two regions stacked vertically. Child
`a` occupies the top region, child `b` the bottom. Default split
is 6/6. Split values are proportional.

Example: `TB(相, 心)` places 相 on top and 心 on bottom.

### 8.4 LR3 (Three-Part Horizontal)

    LR3(a, b, c)
    LR3(a, b, c, split)

Divides the parent box into three side-by-side regions. Default
split is 4/4/4 (equal thirds). Split values are proportional.

Example: `LR3(亻, 木, 木)` for characters with three horizontal
components.

### 8.5 TB3 (Three-Part Vertical)

    TB3(a, b, c)
    TB3(a, b, c, split)

Divides the parent box into three stacked regions. Default split
is 4/4/4 (equal thirds). Split values are proportional.

### 8.6 SUR (Surround)

    SUR(a, b)
    SUR(a, b, side)
    SUR(a, b, side, inset)

Places child `b` inside child `a`, where `a` is a surrounding
structure. The outer component `a` always occupies the full parent
bounding box. The `side` parameter specifies which sides of the
parent box the outer component `a` visually covers. The `inset`
parameter specifies how many grid units the inner component `b`
is inset from the covered sides of the parent bounding box. On
uncovered sides, the inner component extends to the parent edge
(inset 0). Default side is `full`, default inset is `2`.

For `full`, all four sides are inset uniformly. For other side
values, only the sides listed in the table below are inset; the
remaining sides receive no inset. For example, `SUR(广, 木, tl, 2)`
insets the inner box 2 units from the top and 2 units from the
left, but the inner box extends to the parent's right and bottom
edges.

The defined side values are:

| Side    | Description                        | a covers              | Inset applied to       |
|---------|------------------------------------|-----------------------|------------------------|
| `full`  | Full surround (enclosure)          | All four sides        | top, right, bottom, left |
| `tl`    | Top and left                       | Top + left            | top, left              |
| `tr`    | Top and right                      | Top + right           | top, right             |
| `top`   | Top opening at bottom              | Top + left + right    | top, left, right       |
| `right` | Right opening at left              | Top + right + bottom  | top, right, bottom     |
| `left`  | Left opening at right              | Top + left + bottom   | top, left, bottom      |
| `bot`   | Bottom opening at top              | Bottom + left + right | bottom, left, right    |
| `bl`    | Bottom and left                    | Bottom + left         | bottom, left           |
| `br`    | Bottom and right                   | Bottom + right        | bottom, right          |

Example: `SUR(門, 口)` places 口 inside 門 (full surround).

Example: `SUR(广, 木, tl)` places 木 under the top-left shelter
of 广.

### 8.7 OVR (Overlay)

    OVR(a, b)

Places child `b` on top of child `a` within the same bounding box.
Both children occupy the full parent box. OVR is used for
characters where components are superimposed rather than spatially
separated.

Example: `OVR(十, 口)` overlays 口 on 十.

### 8.8 GRP (Group)

    GRP(a, b, ...)

Groups 2 or more child expressions within the same bounding box.
All children occupy the full parent bounding box, as with `OVR`.
GRP exists to avoid deeply nested OVR expressions for characters
with more than two overlaid or superimposed components. Drawing
order follows argument order (first argument drawn first).

A Level 1 parser MUST validate that GRP has at least 2 children.

### 8.9 GRID (2x2 Grid)

    GRID(a, b, c, d)
    GRID(a, b, c, d, hsplit, vsplit)

Divides the parent box into a 2x2 grid. Children are assigned in
reading order: `a` = top-left, `b` = top-right, `c` = bottom-left,
`d` = bottom-right. Each child region becomes a new `[0,0]` to
`[12,12]` coordinate space per Section 5.2.

The optional `hsplit` parameter specifies the horizontal division
(left column width / right column width); the optional `vsplit`
parameter specifies the vertical division (top row height / bottom
row height). Both use the same `SPLIT_2` syntax as `LR` and `TB`
(two integers interpreted proportionally, as with `LR` and `TB`).
Default splits are `6/6` and `6/6`
(equal quadrants). If splits are provided, both MUST be present.

Example: `GRID(口, 口, 口, 口)` for 器-like structures (equal
quadrants).

Example: `GRID(日, 月, 木, 心, 5/7, 4/8)` allocates 5 units to
the left column, 7 to the right, 4 to the top row, and 8 to the
bottom.

---

## 9. Transform Operators

### 9.1 Overview

CSDL defines 3 transform operators that modify the geometry of a
child expression. Transform operators take a single child
expression and produce a modified version within a bounding box.

All transform parameters are bounded integers in the range -12 to
24 inclusive (see §6.9 constraint 3). The upper bound of 24 equals
2× the grid dimension, which is sufficient for all known
composition patterns; exceeding this range suggests a modeling
error. Transform parameters always operate in the 12-unit grid
space, even when applied to children defined in `/24` blocks
(see §5.3).

Scale (`sc`) and skew (`sk`) transforms are applied relative to
the center of the child expression's bounding box (i.e., point
`[6,6]` in the child's coordinate space). Shift (`sh`) is a
translation and has no anchor point.

When transforms are nested, evaluation proceeds inside-out
(standard function composition). In the expression
`sh(sc(expr, sx=8, sy=8), dx=2, dy=0)`, the scale is applied
first to produce an intermediate result, and the shift is then
applied to that result. This is the only permitted evaluation
order; implementations MUST NOT reorder transforms.

### 9.2 sc (Scale)

    sc(expr, sx=N, sy=N)

Scales the child expression. `sx` and `sy` are scale factors
expressed as fractions of 12. A value of 12 means no scaling
(100%), 6 means 50%, 18 means 150%. Scaling is always anchored
at the center of the child's bounding box (`[6,6]`). There is
no anchor parameter; to scale from a corner or edge, compose
`sc` with `sh`:

    sh(sc(口, sx=8, sy=8), dx=4, dy=4)

This scales 口 to 2/3 size (centered) and then shifts the result
to the bottom-right corner.

Example: `sc(口, sx=8, sy=8)` renders 口 at 2/3 size, centered.

### 9.3 sh (Shift)

    sh(expr, dx=N, dy=N)

Shifts the child expression by `dx` grid units horizontally and
`dy` grid units vertically. Positive `dx` shifts right, positive
`dy` shifts down.

Example: `sh(口, dx=2, dy=1)` shifts 口 two units right and one
unit down.

### 9.4 sk (Skew)

    sk(expr, kx=N, ky=N)

Applies a skew transformation. `kx` skews horizontally (positive
values tilt the top to the right), `ky` skews vertically (positive
values tilt the left side downward). Values are in grid units.

Example: `sk(木, kx=1, ky=0)` applies a slight rightward skew to
木.

---

## 10. Component Definitions

### 10.1 Block Form

Components are defined using `@comp` / `@end` delimiters. A
component body takes one of two forms: stroke form or expression
form.

**Stroke form** defines the component from explicit stroke
invocations:

    @comp component_name
    build: s1 s2 s3
    s1 = S(stroke_name [x1,y1] [x2,y2] width)
    s2 = S(stroke_name [x1,y1] [x2,y2] width)
    s3 = S(stroke_name [x1,y1] [x2,y2] width)
    @end

**Expression form** defines the component from a layout or
transform expression over other components (see Section 10.3):

    @comp component_name
    build: from_expr
    LAYOUT_OR_TRANSFORM_EXPR
    @end

The `build:` line specifies explicit stroke ordering (stroke form)
or delegates ordering to the expression structure (expression
form). If the `build:` line is omitted entirely in stroke form,
strokes are drawn in definition order (the order in which
`STROKE_DEF` lines appear in the block).

In stroke form, each stroke definition line assigns a stroke
identifier and a stroke invocation. Stroke identifiers MUST be
unique within the component block. A component block MUST NOT
mix stroke definitions and bare expression lines.

### 10.2 Example: 口 (kou3)

    @comp 口
    build: s1 s2 s3
    s1 = S(shu [3,2] [3,10] 1)
    s2 = S(heng-zhe [3,2] [9,2] [9,10] 1)
    s3 = S(heng [3,10] [9,10] 1)
    @end

### 10.3 Expression Form

A component MAY be defined by a layout or transform expression
over other components, rather than by explicit stroke definitions.
This is the expression form. It uses the `build: from_expr`
marker followed by a single expression line:

    @comp 相
    build: from_expr
    LR(木, 目, 5/7)
    @end

    @comp 寺
    build: from_expr
    TB(土, 寸, 5/7)
    @end

The `build: from_expr` line signals that the component body is a
single CSDL expression, not a list of stroke definitions. The
expression MUST appear on the line immediately following
`build: from_expr`. Exactly one expression line MUST be present.

Expression-form components are structurally equivalent to
expanding the expression inline at every reference site. They
exist for reuse and readability. An implementation MUST evaluate
an expression-form component by recursively resolving the
expression's component references and then applying layout or
transform semantics as usual.

The stroke order of an expression-form component is derived from
its expression using the implicit build order rules in Section 12.2.

The mutual exclusion constraints between stroke form and expression
form (including the `/24` restriction) are specified formally in
Section 6.9, constraints 13-15.

### 10.4 /24 Override

Components requiring fine-grained positioning use the /24 grid:

    @comp 辶.bot /24
    build: s1 s2
    s1 = S(heng-zhe-zhe-pie [2,12] [8,12] [14,18] [6,22] 1)
    s2 = S(na [6,22] [22,16] 1)
    @end

### 10.5 Positional Variants

A component MAY have multiple positional variants, each defined as
a separate `@comp` block with a dotted name:

    @comp 心
    build: s1 s2 s3 s4
    s1 = S(dian [3,5] [4,6] 1)
    s2 = S(wo-gou [1,8] [6,10] [11,6] 1)
    s3 = S(dian [7,3] [8,4] 1)
    s4 = S(dian [10,5] [11,6] 1)
    @end

    @comp 心.left
    build: s1 s2 s3
    s1 = S(dian [3,3] [4,4] 1)
    s2 = S(dian [3,6] [4,7] 1)
    s3 = S(shu [3,9] [3,11] 1)
    @end

When a character definition references `心`, a renderer MAY
substitute `心.left` or `心.bot` based on the structural position.
This substitution is a RECOMMENDATION; it is not required for
conformance. An author who requires a specific variant SHOULD use
the variant name explicitly.

### 10.6 Component-Character Equivalence

When a `@comp` block is defined with a CJK character name (e.g.,
`@comp 口`), that component definition is automatically available
as the character definition for the corresponding Unicode code
point, unless an explicit `@char` definition for that code point
and the same `ortho:` tag exists in the same file. An explicit
`@char` definition takes precedence over an implicit
component-derived definition only when their `ortho:` tags match
(or both lack one). When a `@comp` block and an explicit `@char`
block for the same code point carry distinct `ortho:` tags, both
definitions are valid and the renderer selects between them using
the matching rules in Section E.5.

The multiple-definition-per-code-point rules in Section 4.7.5
apply to implicit character definitions derived from `@comp`
blocks. Specifically: if two `@comp` blocks share the same CJK
character name but carry distinct `ortho:` tags, both implicit
character definitions are valid (the §4.5 last-definition-wins
rule does not apply across distinct ortho tags). If two `@comp`
blocks share the same name and the same `ortho:` tag (or both
lack one), the §4.5 last-definition-wins rule resolves the
component, and the winning definition provides the implicit
character definition. The §4.7.5 rejection rule (duplicate code
point with same ortho tag) applies only to explicit `@char`
definitions.

### 10.7 Aliases

Alias definitions bind an ASCII pinyin name to a Unicode character
name:

    @alias kou3 = 口
    @alias mu4 = 木
    @alias shui3pang2 = 氵

After an alias definition, the pinyin name and the Unicode
character name are interchangeable in all contexts. The
file-order position of an alias definition relative to its
use sites is not significant; aliases MAY appear after the
definitions that reference them.

The right-hand side of an alias definition MUST be a single CJK
character (`CJK_CHAR`), not a compound name or variant. This is
intentional: aliases map ASCII pinyin names to Unicode characters,
not to arbitrary component names. To reference a positional
variant by an ASCII name, place the variant tag on the left-hand
side: `@alias shou3.left = 扌`. An alias like
`@alias foo1 = 心.left` is not valid; use `@alias foo1.left = 忄`
or reference the variant directly by its Unicode character.

An alias name MUST NOT collide with any component name defined
in the same file. That is, if `@alias foo1 = 壹` is present,
there MUST NOT be a `@comp foo1` block in the same file (and
vice versa). A Level 1 parser MUST reject a file that contains
such a collision.

A Level 1 parser with access to pronunciation data (e.g., Unihan
`kMandarin`) SHOULD validate that alias pinyin names match the
standard Mandarin pronunciation of the aliased character. For
example, `@alias kou4 = 口` should generate a warning because 口
is pronounced kǒu (tone 3), not kòu (tone 4). Such warnings are
advisory and do not affect conformance; parsers without
pronunciation data MAY skip this validation.

---

## 11. Character Definitions

### 11.1 Inline Form

The inline form defines a character on a single line:

    CODEPOINT PINYIN_NAME = EXPR [METADATA...]

Examples:

    U+660E ming2 = LR(日, 月)
    U+554F wen4 = SUR(門, 口)
    U+60F3 xiang3 = TB(相, 心)
    U+4EBA ren2 = LR(亻, 寺, 4/8) rad:9 sc:7

### 11.2 Block Form

Characters requiring multiple stroke definitions or complex
internal structure use block form:

    @char U+XXXX pinyin_name
    build: s1 s2 s3 ...
    s1 = S(...)
    s2 = S(...)
    ...
    rad: N
    sc: N
    @end

The body of a `@char` block follows the same structural rules as
a `@comp` block body (Section 10.1). The formal constraints are
in Section 6.9, constraints 21-22.

Characters that require both explicit strokes and compositional
sub-structure SHOULD define the sub-structures as `@comp`
components and reference them from within the `@char` block's
expression.

### 11.3 Metadata

Metadata fields appear after the expression (inline form) or as
separate lines before `@end` (block form). Metadata is
informational; it does not affect evaluation.

Standard metadata fields:

| Field    | Type           | Description                        |
|----------|----------------|------------------------------------|
| `rad:`   | 1-214          | Kangxi radical number              |
| `sc:`    | 1+             | Total stroke count                 |
| `freq:`  | 1+             | Frequency rank                     |
| `ortho:` | tag[,tag,...]  | Orthography tag(s) (Section 4.7)   |

Extension metadata fields MUST use the `x-` prefix:

    U+660E ming2 = LR(日, 月) ortho:Hant rad:72 sc:8 x-grade:2

---

## 12. Build Order Derivation

### 12.1 Explicit Build Order

A `build:` line with stroke identifiers in a `@comp` or `@char`
block specifies the exact stroke order:

    build: s1 s2 s3 s4

Strokes are drawn in the listed order, left to right. All stroke
identifiers referenced in the `build:` line MUST be defined in the
same block.

When an explicit `build:` line is present in a `@comp` or
`@char` block:

- Every stroke identifier listed in the `build:` line MUST
  have a corresponding stroke definition (`STROKE_ID = S(...)`)
  in the same block.
- Every stroke identifier defined in the block MUST appear
  exactly once in the `build:` line.

A Level 1 parser MUST reject a block where these two sets do
not match.

A `build: from_expr` line indicates that the component is defined
by an expression and its stroke order is derived implicitly from
the expression structure (see Section 12.2). Expression-form
components MUST NOT use explicit stroke identifiers in the
`build:` line.

If a stroke-form `@comp` or `@char` block omits the `build:` line
entirely, the stroke order defaults to definition order (the order
in which `STROKE_DEF` lines appear in the block).

### 12.2 Implicit Build Order

When no `build:` line is present, the stroke order is derived from
the expression structure using the following rules, applied
recursively:

1. **Top before bottom.** In a `TB` or `TB3` layout, the top
   child's strokes precede the bottom child's strokes.
2. **Left before right.** In an `LR` or `LR3` layout, the left
   child's strokes precede the right child's strokes.
3. **Outside before inside.** In a `SUR` layout, the outer
   component's strokes precede the inner component's strokes.
4. **Inside before closing stroke.** Exception to rule 3: if the
   outer component of a `SUR` has an identified closing stroke,
   the inner component's strokes are drawn before the closing
   stroke. A closing stroke is identified by a `close:` marker
   in the outer component's `@comp` block (see Section 12.4).
   If no `close:` marker is present, rule 3 applies without
   exception.
5. **GRP and OVR order.** For `GRP` and `OVR` layouts, strokes
   are drawn in argument order (left to right in the expression).
6. **GRID order.** Reading order: top-left, top-right,
   bottom-left, bottom-right.

### 12.3 Algorithm

```
function derive_order(node):
    if node is STROKE:
        return [node]
    if node is COMP_REF:
        return derive_order(resolve(node))
    if node is TRANSFORM:
        return derive_order(node.child)
    if node is LAYOUT:
        result = []
        for child in node.children (in structural order per rules above):
            result.extend(derive_order(child))
        if node is SUR and outer_has_close_marker(node.outer):
            closing = result.pop(closing_stroke_index)
            inner_end = index_after_inner_strokes(result)
            result.insert(inner_end, closing)
        return result
```

### 12.4 Closing Stroke Marker

A `@comp` block MAY include a `close:` line identifying the
stroke that serves as the closing stroke of an enclosure:

    @comp 囗
    build: s1 s2 s3
    close: s3
    s1 = S(shu [2,1] [2,11] 1)
    s2 = S(heng-zhe [2,1] [10,1] [10,11] 1)
    s3 = S(heng [2,11] [10,11] 1)
    @end

The `close:` value MUST be a stroke identifier defined in the
same block. When this component is used as the outer argument of
a `SUR` operator and implicit build order is in effect, the
closing stroke is moved after the inner component's strokes per
rule 4 in Section 12.2.

If no `close:` marker is present, the SUR build order applies
rule 3 uniformly (all outer strokes before all inner strokes).
The `close:` marker is OPTIONAL; its absence produces
deterministic behavior. Authors who care about pedagogically
correct stroke order for enclosure characters SHOULD use it.

---

## 13. Extensibility

### 13.1 Safe Additions

Future versions of this specification MAY add:

- New metadata fields (without the `x-` prefix).
- New entries in the stroke registry (both base and compound),
  provided they do not conflict with existing names.
- New orthography tags in the Appendix E registry.

Variant tags (`VARIANT_TAG`) are already open-ended and do not
require specification-level additions. Authors MAY introduce new
variant tags as needed.

A Level 1 parser that encounters an unknown metadata field SHOULD
issue a warning and continue processing. A Level 1 parser that
encounters an unknown `ortho:` tag SHOULD issue a warning and
continue processing.

### 13.2 Forbidden Additions

Future versions of this specification MUST NOT add:

- Variables, conditionals, loops, or any Turing-complete features.
- Macros or template expansion.
- Runtime composition of compound strokes from base strokes.
- Any feature that would make evaluation non-terminating or
  non-deterministic.
- Any feature that would require more than a single evaluation
  pass.

These constraints are fundamental to the language design and MUST
be preserved across all versions.

### 13.3 Script Extension Hooks

CSDL's stroke inventory (Section 7) is designed for Han-derived
scripts. Structurally adjacent scripts (Tangut, Khitan, Jurchen,
Sawndip, classical Yi, and others) may require stroke primitives
not present in the current registry.

Authors working with these scripts SHOULD use the `x-` extension
mechanism for both orthography tags and (where necessary) custom
metadata to identify non-standard stroke usage:

    @ortho x-Tang
    @comp 𗁅
    build: s1 s2 s3
    s1 = S(heng [2,3] [10,3] 1)
    ...
    ortho: x-Tang
    x-stroke-ext: tangut-pie-gou
    @end

Future versions of this specification MAY promote `x-` extension
tags to standard tags and MAY extend the stroke registry with
new primitives required by these scripts. Such extensions MUST
NOT modify the semantics of existing stroke names or operators.

A Level 1 parser MUST accept `x-` prefixed orthography tags
without validation of the tag value beyond syntactic conformance.
A Level 2 renderer SHOULD treat unknown `x-` orthography tags as
opaque identifiers for filtering purposes.

---

## 14. Security Considerations

CSDL is a declarative description language with no executable code,
no I/O, no network access, and no external process invocation.
Evaluation is bounded: the number of strokes, tree depth, and
coordinate computations in the output are all linear in the input
size. There is no mechanism by which a CSDL input can cause
superlinear resource consumption.

Implementations SHOULD be capable of processing files covering
the standard CJK Unified Ideographs repertoire (the approximately
98,000 characters encoded across all CJK Unified Ideographs blocks
in the referenced Unicode version) and component reference depths
typical of that repertoire. Implementations MAY impose stricter
limits for constrained environments but SHOULD document them.

---

## 15. References

### 15.1 Normative References

**[BCP 14]**
Best Current Practice 14. Comprises RFC 2119 and RFC 8174.

**[RFC 2119]**
Bradner, S., "Key words for use in RFCs to Indicate Requirement
Levels", BCP 14, RFC 2119, March 1997.

**[RFC 8174]**
Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119
Key Words", BCP 14, RFC 8174, May 2017.

**[RFC 3629]**
Yergeau, F., "UTF-8, a transformation format of ISO 10646",
STD 63, RFC 3629, November 2003.

**[BCP 47]**
Phillips, A. and M. Davis, "Tags for Identifying Languages",
BCP 47, RFC 5646, September 2009.
https://www.rfc-editor.org/info/bcp47

**[RFC 4647]**
Phillips, A. and M. Davis, "Matching of Language Tags",
RFC 4647, September 2006.
https://www.rfc-editor.org/info/rfc4647

**[Unicode]**
The Unicode Consortium, "The Unicode Standard", Version 16.0.0
(or later). https://www.unicode.org/versions/latest/

**[UAX #15]**
The Unicode Consortium, "Unicode Standard Annex #15: Unicode
Normalization Forms".
https://www.unicode.org/reports/tr15/

**[W3C XML]**
Bray, T. et al., "Extensible Markup Language (XML) 1.0 (Fifth
Edition)", W3C Recommendation, November 2008. Section 6:
Notation. https://www.w3.org/TR/xml/#sec-notation

### 15.2 Media Type

The proposed media type is `text/csdl` with file extension `.csdl`,
encoded as UTF-8 without BOM. IANA registration is deferred until
specification stability warrants it.

### 15.3 Companion Documents

**[CSDL-IMPL]**
CSDL Implementor's Checklist, Version 1.0 Draft, 2026-02-09.
File: `csdl-implementors-checklist-v1_0.md`

**[CSDL-PRIMER]**
CSDL Primer — A Human-Writable Guide, Version 1.0 Draft,
2026-02-09. File: `csdl-primer-v1_0.md`

### 15.4 Informative References

**[IDS]**
The Unicode Consortium, "Unicode Standard Annex #45: U-Source
Ideographs", https://www.unicode.org/reports/tr45/

**[Kangxi]**
Kangxi Dictionary (康熙字典), 1716. Radical system of 214
radicals.

**[OpenType]**
Microsoft Corporation, "OpenType Specification",
https://learn.microsoft.com/en-us/typography/opentype/spec/

**[CHISE]**
CHISE Project, "Character Processing Based on Character
Ontology", https://www.chise.org/

### 15.5 Feedback and Errata

Feedback, errata, and issue reports:
https://github.com/MarkAtwood/spec-csdl/issues

---

## Appendix A: IDS Operator Mapping

This appendix maps Unicode Ideographic Description Characters to
CSDL layout operators. This mapping enables mechanical translation
from IDS sequences to CSDL expressions.

| IDS Char | Code Point | IDS Name                | CSDL Operator       |
|----------|------------|-------------------------|---------------------|
| ⿰       | U+2FF0     | Left to Right           | `LR(a, b)`          |
| ⿱       | U+2FF1     | Above to Below          | `TB(a, b)`          |
| ⿲       | U+2FF2     | Left to Middle to Right | `LR3(a, b, c)`      |
| ⿳       | U+2FF3     | Above to Middle to Below| `TB3(a, b, c)`      |
| ⿴       | U+2FF4     | Full Surround           | `SUR(a, b, full)`   |
| ⿵       | U+2FF5     | Surround from Above     | `SUR(a, b, top)`    |
| ⿶       | U+2FF6     | Surround from Below     | `SUR(a, b, bot)`    |
| ⿷       | U+2FF7     | Surround from Left      | `SUR(a, b, left)`   |
| ⿸       | U+2FF8     | Surround Upper Left     | `SUR(a, b, tl)`     |
| ⿹       | U+2FF9     | Surround Upper Right    | `SUR(a, b, tr)`     |
| ⿺       | U+2FFA     | Surround Lower Left     | `SUR(a, b, bl)`     |
| ⿻       | U+2FFB     | Overlaid                | `OVR(a, b)`         |

Note: IDS has no equivalents for CSDL's `GRP` and `GRID` operators,
or for the `right` and `br` surround sides.
Characters requiring these operators cannot be round-tripped through
IDS without information loss.

---

## Appendix B: Kangxi Radical Registry (Representative)

This appendix provides a representative sample of the Kangxi 214
radical registry. The full registry is a companion document.

| Rad# | Char | Pinyin      | Strokes | Meaning         | Variants         | Typical Position(s) |
|------|------|-------------|---------|-----------------|------------------|---------------------|
| 1    | 一   | yi1         | 1       | one             |                  | top, bot, component |
| 4    | 丿   | pie3        | 1       | slash           |                  | component           |
| 9    | 人   | ren2        | 2       | person          | 亻 ren2.left     | left                |
| 18   | 刀   | dao1        | 2       | knife           | 刂 dao1.right    | right               |
| 30   | 口   | kou3        | 3       | mouth           |                  | left, bot, inner    |
| 32   | 土   | tu3         | 3       | earth           |                  | left, bot           |
| 40   | 宀   | mian2       | 3       | roof            |                  | top                 |
| 61   | 心   | xin1        | 4       | heart           | 忄 xin1.left, 心.bot | left, bot       |
| 64   | 手   | shou3       | 4       | hand            | 扌 shou3.left    | left                |
| 72   | 日   | ri4         | 4       | sun             |                  | left, top           |
| 75   | 木   | mu4         | 4       | tree            |                  | left, top, bot      |
| 85   | 水   | shui3       | 4       | water           | 氵 shui3.left    | left                |
| 118  | 竹   | zhu2        | 6       | bamboo          | ⺮ zhu2.top      | top                 |
| 130  | 肉   | rou4        | 6       | meat            | 月 rou4.left     | left                |
| 140  | 艸   | cao3        | 6       | grass           | 艹 cao3.top      | top                 |
| 149  | 言   | yan2        | 7       | speech          | 讠 yan2.left     | left                |
| 162  | 辶   | chuo4       | 7       | walk            | 辶.bot           | bot-left surround   |
| 163  | 邑   | yi4         | 7       | city            | 阝 yi4.right     | right               |
| 167  | 金   | jin1        | 8       | gold/metal      | 钅 jin1.left     | left                |
| 170  | 阜   | fu4         | 8       | mound           | 阝 fu4.left      | left                |

Note on radicals 163/170: Both use the component 阝 but in
different positions. Radical 163 (邑, city) appears on the right
as 阝 yi4.right. Radical 170 (阜, mound) appears on the left as
阝 fu4.left. CSDL disambiguates these via positional variant names.

Note on radical 74/130: 月 (moon, radical 74) and the left
variant of 肉 (meat, radical 130) are graphically identical in
modern typefaces. CSDL treats disambiguation as the author's
responsibility. Authors SHOULD use `rou4.left` when the semantic
radical is meat, and `月` or `yue4` when the semantic radical is
moon.

### Pinyin Collision Note

Several radicals share the same pinyin reading (e.g., radical
69 斤 and radical 167 金 are both `jin1`; radical 22 匚 and
radical 70 方 are both `fang1`). The pinyin values in this
registry are informational labels for human readers. They do
not automatically generate CSDL aliases or component names.

Authors who create pinyin-based aliases for colliding radicals
MUST use distinct names. The CSDL variant tag mechanism
provides a natural disambiguation path (e.g., `jin1.axe` for
斤, `jin1.metal` for 金). Per the CSDL specification, each
alias name MUST be unique within a file.

---

## Appendix C: Compound Stroke Enumeration

Each compound stroke is assigned a registry identifier C01-C26 for
reference in tooling and interchange formats.

### C.1 Single-Fold Compounds (12)

| ID  | Name       | Segments      | Points | Description                        |
|-----|------------|---------------|--------|------------------------------------|
| C01 | heng-zhe   | heng + zhe    | 3      | Horizontal, sharp turn down        |
| C02 | heng-pie   | heng + pie    | 3      | Horizontal, left-falling           |
| C03 | heng-gou   | heng + gou    | 3      | Horizontal, hook down              |
| C04 | shu-zhe    | shu + zhe     | 3      | Vertical, sharp turn right         |
| C05 | shu-wan    | shu + wan     | 3      | Vertical, smooth bend right        |
| C06 | shu-ti     | shu + ti      | 3      | Vertical, rising turn              |
| C07 | shu-gou    | shu + gou     | 3      | Vertical, hook left                |
| C08 | pie-zhe    | pie + zhe     | 3      | Left-falling, sharp turn right     |
| C09 | pie-dian   | pie + dian    | 3      | Left-falling, dot                  |
| C10 | wan-gou    | wan + gou     | 3      | Bend, hook                         |
| C11 | xie-gou    | xie + gou     | 3      | Slant, hook                        |
| C12 | wo-gou     | wo + gou      | 3      | Reclining, hook                    |

### C.2 Double-Fold Compounds (8)

| ID  | Name           | Segments          | Points | Description                    |
|-----|----------------|-------------------|--------|--------------------------------|
| C13 | heng-zhe-zhe   | heng + zhe + zhe  | 4      | H-turn-turn (zigzag)           |
| C14 | heng-zhe-wan   | heng + zhe + wan  | 4      | H-turn-bend                    |
| C15 | heng-zhe-ti    | heng + zhe + ti   | 4      | H-turn-rise                    |
| C16 | heng-zhe-gou   | heng + zhe + gou  | 4      | H-turn-hook                    |
| C17 | heng-xie-gou   | heng + xie + gou  | 4      | H-slant-hook                   |
| C18 | shu-zhe-zhe    | shu + zhe + zhe   | 4      | V-turn-turn                    |
| C19 | shu-zhe-pie    | shu + zhe + pie   | 4      | V-turn-leftfall                |
| C20 | shu-wan-gou    | shu + wan + gou   | 4      | V-bend-hook                    |

### C.3 Triple-Fold Compounds (5)

| ID  | Name               | Segments              | Points | Description              |
|-----|--------------------|-----------------------|--------|--------------------------|
| C21 | heng-zhe-zhe-zhe   | heng + zhe + zhe + zhe| 5      | H-turn-turn-turn         |
| C22 | heng-zhe-zhe-pie   | heng + zhe + zhe + pie| 5      | H-turn-turn-leftfall     |
| C23 | heng-zhe-wan-gou   | heng + zhe + wan + gou| 5      | H-turn-bend-hook         |
| C24 | heng-pie-wan-gou   | heng + pie + wan + gou| 5      | H-leftfall-bend-hook     |
| C25 | shu-zhe-zhe-gou    | shu + zhe + zhe + gou | 5      | V-turn-turn-hook         |

### C.4 Quadruple-Fold Compounds (1)

| ID  | Name                   | Segments                  | Points | Description          |
|-----|------------------------|---------------------------|--------|----------------------|
| C26 | heng-zhe-zhe-zhe-gou   | heng + zhe + zhe + zhe + gou | 6  | H-turn-turn-turn-hook|

### C.5 Summary

| Category         | Count | Point Range |
|------------------|-------|-------------|
| Base strokes     | 11    | 2           |
| Single-fold      | 12    | 3           |
| Double-fold      | 8     | 4           |
| Triple-fold      | 5     | 5           |
| Quadruple-fold   | 1     | 6           |
| **Total**        | **37**| **2-6**     |

---

## Appendix D: Complete Example File

```csdl
# CSDL Example File
# Demonstrates aliases, component definitions, character definitions,
# and orthography tags

@csdl 1.0

# File-level orthography: Traditional Chinese unless overridden
@ortho Hant

# ============================================================
# Aliases
# ============================================================

@alias kou3 = 口
@alias ri4 = 日
@alias yue4 = 月
@alias mu4 = 木
@alias xin1 = 心
@alias shou3.left = 扌
@alias shui3.left = 氵
@alias ren2.left = 亻
@alias yan2.left = 讠

# ============================================================
# Component Definitions
# ============================================================

# 口 mouth (3 strokes)
@comp 口
build: s1 s2 s3
s1 = S(shu [3,2] [3,10] 1)
s2 = S(heng-zhe [3,2] [9,2] [9,10] 1)
s3 = S(heng [3,10] [9,10] 1)
@end

# 一 one (1 stroke)
@comp 一
build: s1
s1 = S(heng [1,6] [11,6] 1)
@end

# 十 cross (2 strokes)
@comp 十
build: s1 s2
s1 = S(heng [2,6] [10,6] 1)
s2 = S(shu [6,2] [6,10] 1)
@end

# 土 earth (3 strokes)
@comp 土
build: s1 s2 s3
s1 = S(heng [3,4] [9,4] 1)
s2 = S(shu [6,2] [6,10] 1)
s3 = S(heng [2,10] [10,10] 1)
@end

# 目 eye (5 strokes)
@comp 目
build: s1 s2 s3 s4 s5
s1 = S(shu [3,1] [3,11] 1)
s2 = S(heng-zhe [3,1] [9,1] [9,11] 1)
s3 = S(heng [3,4] [9,4] 1)
s4 = S(heng [3,7] [9,7] 1)
s5 = S(heng [3,11] [9,11] 1)
@end

# 寸 inch (3 strokes)
@comp 寸
build: s1 s2 s3
s1 = S(heng [2,4] [10,4] 1)
s2 = S(shu-gou [8,1] [8,10] [6,8] 1)
s3 = S(dian [9,7] [10,8] 1)
@end

# 也 also (3 strokes)
@comp 也
build: s1 s2 s3
s1 = S(heng-zhe-gou [2,4] [6,4] [6,10] [4,8] 1)
s2 = S(shu [6,1] [6,10] 1)
s3 = S(shu-wan-gou [9,1] [9,8] [10,10] [11,9] 1)
@end

# 丁 nail (2 strokes)
@comp 丁
build: s1 s2
s1 = S(heng [2,2] [10,2] 1)
s2 = S(shu-gou [6,2] [6,10] [4,8] 1)
@end

# 广 shelter (3 strokes)
@comp 广
build: s1 s2 s3
s1 = S(dian [5,1] [6,2] 1)
s2 = S(heng [2,3] [10,3] 1)
s3 = S(pie [4,3] [1,11] 1)
@end

# 囗 enclosure (3 strokes — used in 國/国)
@comp 囗
build: s1 s2 s3
close: s3
s1 = S(shu [2,1] [2,11] 1)
s2 = S(heng-zhe [2,1] [10,1] [10,11] 1)
s3 = S(heng [2,11] [10,11] 1)
@end

# 艹 grass radical, top variant (3 strokes)
@comp 艹
build: s1 s2 s3
s1 = S(heng [2,6] [10,6] 1)
s2 = S(shu [4,2] [4,6] 1)
s3 = S(shu [8,2] [8,6] 1)
@end

# 日 sun (4 strokes)
@comp 日
build: s1 s2 s3 s4
s1 = S(shu [3,1] [3,11] 1)
s2 = S(heng-zhe [3,1] [9,1] [9,11] 1)
s3 = S(heng [3,6] [9,6] 1)
s4 = S(heng [3,11] [9,11] 1)
@end

# 月 moon (4 strokes)
@comp 月
build: s1 s2 s3 s4
s1 = S(pie [3,1] [1,11] 1)
s2 = S(heng-zhe-gou [3,1] [9,1] [9,11] [3,11] 1)
s3 = S(heng [4,4] [8,4] 1)
s4 = S(heng [4,7] [8,7] 1)
@end

# 木 tree (4 strokes)
@comp 木
build: s1 s2 s3 s4
s1 = S(heng [2,4] [10,4] 1)
s2 = S(shu [6,1] [6,11] 1)
s3 = S(pie [6,4] [2,10] 1)
s4 = S(na [6,4] [10,10] 1)
@end

# 心 heart, standard position (4 strokes)
@comp 心
build: s1 s2 s3 s4
s1 = S(dian [3,5] [4,6] 1)
s2 = S(wo-gou [1,8] [6,10] [11,6] 1)
s3 = S(dian [7,3] [8,4] 1)
s4 = S(dian [10,5] [11,6] 1)
@end

# 心 heart, left variant (忄) (3 strokes)
@comp 心.left
build: s1 s2 s3
s1 = S(dian [5,2] [6,4] 1)
s2 = S(dian [4,5] [5,7] 1)
s3 = S(shu [6,1] [6,11] 1)
@end

# 門 gate (8 strokes)
@comp 門
build: s1 s2 s3 s4 s5 s6 s7 s8
s1 = S(shu [2,1] [2,11] 1)
s2 = S(heng-zhe-gou [2,1] [5,1] [5,11] [2,11] 1)
s3 = S(dian [3,3] [4,4] 1)
s4 = S(shu [5,1] [5,4] 1)
s5 = S(shu [10,1] [10,11] 1)
s6 = S(heng-zhe-gou [5,1] [10,1] [10,11] [5,11] 1)
s7 = S(dian [7,3] [8,4] 1)
s8 = S(shu [8,1] [8,4] 1)
@end

# 相 mutual (9 strokes)
@comp 相
build: from_expr
LR(木, 目, 5/7)
@end

# 亻 person radical, left variant (2 strokes)
@comp 亻
build: s1 s2
s1 = S(pie [6,1] [2,7] 1)
s2 = S(shu [5,4] [5,11] 1)
@end

# 寺 temple (6 strokes)
@comp 寺
build: from_expr
TB(土, 寸, 5/7)
@end

# ============================================================
# Character Definitions: Inline Form
# ============================================================

# Simple left-right (inherits file-level ortho:Hant)
U+660E ming2 = LR(日, 月) rad:72 sc:8

# Simple top-bottom
U+60F3 xiang3 = TB(相, 心) rad:61 sc:13

# Surround (full enclosure)
U+554F wen4 = SUR(門, 口) rad:30 sc:11

# Left-right with custom split
U+5BFA si4 = LR(亻, 寺, 4/8) rad:9 sc:8

# Three-part horizontal
U+6C60 chi2 = LR(氵, 也, 4/8) rad:85 sc:6

# Top-bottom with three parts
U+8349 cao3 = TB(艹, TB(日, 十), 3/9) rad:140 sc:9

# Surround with side specification
U+5E7F guang3_header = SUR(广, 木, tl) rad:53 sc:3

# ============================================================
# Character Definition: Block Form (Stroke)
# ============================================================

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

# ============================================================
# Character Definition: Block Form (Expression)
# ============================================================

@char U+8A69 shi1
build: from_expr
LR(言, 寺, 5/7)
rad: 149
sc: 13
@end

# ============================================================
# Orthography Tag Examples
# ============================================================

# Same character, different orthographies:
# Traditional Chinese 門 (8 strokes) vs Simplified Chinese 门 (3 strokes)
U+9580 men2 = SUR(門, 口) ortho:Hant rad:169 sc:8

# Character valid in both Traditional and Japanese contexts
U+6797 lin2 = LR(木, 木) ortho:Hant,Jpan rad:75 sc:8

# Japanese-specific: Shinjitai form
U+4E07 wan4 = TB(一, 丁) ortho:x-Shin rad:1 sc:3
```

---

## Appendix E: Orthography Tag Registry

This appendix defines the orthography tags recognized by CSDL.
Tags are drawn from the IANA Language Subtag Registry (per BCP 47,
ISO 15924) where available. CSDL extension tags use the `x-`
prefix for scripts not yet assigned standard subtags or where the
BCP 47 tag does not capture the needed distinction.

### E.1 Primary Tags (BCP 47 Script Subtags)

CSDL recognizes the following script subtags from the IANA
Language Subtag Registry [BCP 47] as primary orthography tags.
Implementations MUST accept these tags; additional BCP 47 script
subtags MAY be accepted but are not required.

| Tag    | Script Name                          | CSDL Usage                           |
|--------|--------------------------------------|--------------------------------------|
| `Hant` | Han (Traditional variant)            | Traditional Chinese (TW, HK, MO)    |
| `Hans` | Han (Simplified variant)             | Simplified Chinese (CN, SG, MY)      |
| `Jpan` | Japanese (Han + Hiragana + Katakana) | Japanese Kanji only                  |
| `Kore` | Korean (Hangul + Han)                | Korean Hanja only                    |
| `Hani` | Han (unspecified variant)            | Orthography-neutral Han              |

`Jpan` and `Kore` are BCP 47 tags for full writing systems that
include non-ideographic scripts (Kana, Hangul). In CSDL, these
tags apply only to the Han ideographic subset; CSDL does not
describe Kana or Hangul.

`Hani` indicates a definition valid across multiple Han
orthographies. It is semantically equivalent to omitting the
`ortho:` tag but provides explicit intent.

### E.2 Extended Primary Tags (BCP 47, Non-Han)

These BCP 47 script subtags cover scripts structurally adjacent
to Han that share the stroke-based composition model. The current
CSDL stroke inventory (Section 7) may only partially cover these
scripts.

| Tag    | Script Name | Coverage Status                                |
|--------|-------------|------------------------------------------------|
| `Yiii` | Yi          | Classical Yi ideographs; partial stroke coverage |

### E.3 CSDL Extension Tags

These tags use the `x-` prefix for scripts that either lack
ISO 15924 codes, lack BCP 47 subtags, or require distinctions
finer than BCP 47 provides. Extension tags are provisional; they
MAY be promoted to standard tags in future versions if the
corresponding ISO 15924 codes become available.

| Tag        | Script Name              | Unicode Block(s)                  | Coverage Status           |
|------------|--------------------------|-----------------------------------|---------------------------|
| `x-Nom`    | Vietnamese Chữ Nôm      | U+20000..U+2FA1F (partial)        | Han stroke inventory applies |
| `x-Tang`   | Tangut                   | U+17000..U+187FF, U+18D00..U+18D7F | May need stroke extensions |
| `x-Khit`   | Khitan (large script)    | U+18B00..U+18CFF                  | May need stroke extensions |
| `x-Jurc`   | Jurchen                  | Not yet fully encoded             | May need stroke extensions |
| `x-Sawb`   | Zhuang Sawndip           | Scattered CJK Ext blocks          | Han stroke inventory applies |
| `x-HantHK` | Trad. Chinese (Hong Kong)| Same as Hant                      | HK glyph variants          |
| `x-HantTW` | Trad. Chinese (Taiwan)   | Same as Hant                      | TW glyph variants          |
| `x-Kyuj`   | Japanese Kyūjitai        | Same as Jpan                      | Pre-reform Japanese forms   |
| `x-Shin`   | Japanese Shinjitai       | Same as Jpan                      | Post-reform Japanese forms  |

Note on `x-HantHK` and `x-HantTW`: These sub-regional tags exist
because Hong Kong and Taiwan have distinct standard glyph forms
for some characters (e.g., the bottom component of 骨). Use `Hant`
when the distinction is irrelevant. Use `x-HantHK` or `x-HantTW`
only when the definition targets a specific regional standard.

Note on `x-Kyuj` and `x-Shin`: Japanese Kanji underwent
simplification reforms in 1946 and 1981. `x-Kyuj` designates
pre-reform (old form) glyphs; `x-Shin` designates post-reform
(new form) glyphs. Use `Jpan` when the distinction is irrelevant.

### E.4 Tag Selection Guide

When annotating a definition, authors SHOULD select the most
specific applicable tag:

1. If the definition is specific to a national or regional
   standard glyph form, use the corresponding tag (e.g.,
   `x-HantTW`, `x-Shin`).
2. If the definition is specific to a script tradition but not a
   particular region, use the primary tag (e.g., `Hant`, `Hans`,
   `Jpan`).
3. If the definition is valid across all Han orthographies, use
   `Hani` or omit the tag.
4. If the definition belongs to a non-Han script, use the
   appropriate extended or `x-` tag.

### E.5 Renderer Matching Rules

When a renderer has a target orthography and must select among
multiple definitions for the same code point, renderers SHOULD
apply the Basic Filtering algorithm defined in [RFC 4647] §3.3,
treating the `ortho:` tag as the tag and the renderer's target
orthography as the range, using the parent-child relationships
in Table E.5.

If no definition matches at any level, the renderer SHOULD use
any available definition and MAY issue a warning.

Table E.5: Parent-child relationships for tag matching:

| Child Tag    | Parent Tag |
|--------------|------------|
| `x-HantHK`  | `Hant`     |
| `x-HantTW`  | `Hant`     |
| `x-Kyuj`    | `Jpan`     |
| `x-Shin`    | `Jpan`     |
| `Hant`       | `Hani`     |
| `Hans`       | `Hani`     |
| `Jpan`       | `Hani`     |
| `Kore`       | `Hani`     |
| `x-Nom`     | `Hani`     |
| `x-Sawb`    | `Hani`     |

Scripts without a parent relationship (`x-Tang`, `x-Khit`,
`x-Jurc`, `Yiii`) have no fallback hierarchy. A renderer MUST NOT
fall back from one of these to a Han definition.

---

*End of CSDL Specification*
