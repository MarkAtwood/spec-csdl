# CSDL-U Annotation Syntax

**Status:** Draft
**Version:** 0.1
**Date:** 2026-06-21

---

## 1. Overview

CSDL-U is the Unicode-native syntax profile of CSDL. It uses Ideographic
Description Characters (U+2FF0-U+2FFB) as layout operators, enabling
delimiter-free prefix notation. However, standard IDS lacks features that
CSDL-ASCII provides:

- Split ratios for layout operators
- Transform operators (scale, shift, skew)
- GRP (group) operator for multi-component overlay
- GRID operator for 2x2 layouts

This document specifies annotation syntax that extends basic IDS with
these CSDL features while maintaining:

1. **Unambiguity** - No parsing conflicts with IDS or Unicode text
2. **Unicode-friendliness** - Minimal ASCII, prefer Unicode operators
3. **Composability** - Annotations can be combined and nested

---

## 2. Design Principles

### 2.1 Annotation Attachment

Annotations modify the immediately preceding element. An "element" is:
- A single CJK character: `木`
- An IDS operator with its operands: `⿰日月`
- A parenthesized group: `(⿰日月)`

Annotations bind tightly. `⿰ab:4/8` means the split applies to the
LR composition, not to `b` alone. When ambiguity could arise, use
parentheses: `⿰a(b:4/8)` would (incorrectly) attempt to apply a split
to `b`, which is invalid.

### 2.2 Delimiter Selection

CSDL-U uses Unicode delimiters from mathematical and technical blocks
to avoid conflicts with:
- ASCII punctuation used in other contexts (URLs, prose)
- CJK punctuation (which might appear in component names)
- IDS characters (U+2FF0-U+2FFB)

Selected delimiters:

| Role | Character | Code Point | Name |
|------|-----------|------------|------|
| Split prefix | `∶` | U+2236 | RATIO |
| Transform prefix | `⊛` | U+229B | CIRCLED ASTERISK OPERATOR |
| Fraction separator | `⁄` | U+2044 | FRACTION SLASH |
| Group open | `⟦` | U+27E6 | MATHEMATICAL LEFT WHITE SQUARE BRACKET |
| Group close | `⟧` | U+27E7 | MATHEMATICAL RIGHT WHITE SQUARE BRACKET |
| Grid operator | `⊞` | U+229E | SQUARED PLUS |
| Parameter separator | `⹁` | U+2E41 | REVERSED COMMA |

### 2.3 ASCII Fallback

For environments where Unicode input is difficult, ASCII equivalents
are permitted:

| Unicode | ASCII Fallback |
|---------|----------------|
| `∶` | `:` (COLON) |
| `⁄` | `/` (SOLIDUS) |
| `⊛` | `@` (COMMERCIAL AT) |
| `⟦` | `[[` |
| `⟧` | `]]` |
| `⊞` | `[+]` |
| `⹁` | `,` (COMMA) |

A conformant CSDL-U parser MUST accept both Unicode and ASCII forms.
The Unicode forms are canonical for interchange; the ASCII forms are
input conveniences.

---

## 3. Split Ratio Syntax

### 3.1 Grammar

```ebnf
(* Split annotation *)
SPLIT_ANN   ::= RATIO_DELIM SPLIT_VAL
RATIO_DELIM ::= '∶' | ':'
SPLIT_VAL   ::= UINT FRAC_SEP UINT ( FRAC_SEP UINT )?
FRAC_SEP    ::= '⁄' | '/'
UINT        ::= [0-9]+
```

### 3.2 Semantics

A split annotation specifies proportional division of the parent
bounding box. For binary operators (LR, TB), two values are required.
For ternary operators (LR3, TB3), three values are required.

Split values are proportional. `∶4⁄8` divides in ratio 4:8 (equivalently
1:2). Values summing to 12 align with CSDL grid boundaries but this
is not required.

### 3.3 Examples

| CSDL-ASCII | CSDL-U | Notes |
|------------|--------|-------|
| `LR(a, b)` | `⿰ab` | Default 6/6 split |
| `LR(a, b, 4/8)` | `⿰ab∶4⁄8` | 4:8 ratio |
| `TB(a, b, 3/9)` | `⿱ab∶3⁄9` | 3:9 ratio |
| `LR3(a, b, c, 3/5/4)` | `⿲abc∶3⁄5⁄4` | Three-way split |
| `TB3(a, b, c)` | `⿳abc` | Default 4/4/4 split |

### 3.4 Scope

Split annotations apply to binary and ternary layout operators only:
- `⿰` (LR)
- `⿱` (TB)
- `⿲` (LR3)
- `⿳` (TB3)

SUR operators have inset parameters, not splits. GRID has its own
split syntax (see Section 6).

---

## 4. Transform Syntax

### 4.1 Grammar

```ebnf
(* Transform annotation *)
XFORM_ANN   ::= XFORM_DELIM XFORM_OP '(' XFORM_PARAMS ')'
XFORM_DELIM ::= '⊛' | '@'
XFORM_OP    ::= 'sc' | 'sh' | 'sk'
XFORM_PARAMS::= PARAM_PAIR ( PARAM_SEP PARAM_PAIR )*
PARAM_PAIR  ::= PARAM_NAME '=' TPARAM
PARAM_SEP   ::= '⹁' | ','
PARAM_NAME  ::= 'sx' | 'sy' | 'dx' | 'dy' | 'kx' | 'ky'
TPARAM      ::= '-'? [0-9]+   (* range: -12 to 24 *)
```

### 4.2 Semantics

Transform annotations apply geometric transforms to the preceding
element:

- **`sc(sx=N⹁sy=M)`** - Scale by sx/12 horizontally, sy/12 vertically.
  12 = no scaling, 6 = 50%, 18 = 150%. Anchored at center [6,6].

- **`sh(dx=N⹁dy=M)`** - Shift by dx grid units right, dy units down.
  Negative values shift left/up.

- **`sk(kx=N⹁ky=M)`** - Skew by kx units horizontally (positive tilts
  top rightward), ky units vertically (positive tilts left downward).

### 4.3 Examples

| CSDL-ASCII | CSDL-U | Notes |
|------------|--------|-------|
| `sc(口, sx=8, sy=8)` | `口⊛sc(sx=8⹁sy=8)` | Scale to 2/3 |
| `sh(口, dx=2, dy=1)` | `口⊛sh(dx=2⹁dy=1)` | Shift right+down |
| `sk(木, kx=1, ky=0)` | `木⊛sk(kx=1⹁ky=0)` | Slight skew |
| `sh(sc(口, sx=8, sy=8), dx=4, dy=4)` | `口⊛sc(sx=8⹁sy=8)⊛sh(dx=4⹁dy=4)` | Chained transforms |

### 4.4 Chained Transforms

Multiple transform annotations chain left-to-right, with inner
transforms applied first. This matches standard function composition
order (inside-out):

```
口⊛sc(sx=8⹁sy=8)⊛sh(dx=4⹁dy=4)
```

Evaluation: scale 口 first, then shift the scaled result.

Equivalent CSDL-ASCII:
```
sh(sc(口, sx=8, sy=8), dx=4, dy=4)
```

### 4.5 Transforms on Compound Expressions

To apply a transform to a compound IDS expression, parenthesize the
expression:

```
(⿰日月)⊛sc(sx=8⹁sy=8)
```

Without parentheses, the transform would attach to `月` alone.

---

## 5. GRP (Group) Operator

### 5.1 Rationale

IDS has no equivalent for CSDL's GRP operator, which overlays 2 or
more components in the same bounding box with explicit ordering.
While OVR (`⿻`) handles two components, deeply nested `⿻⿻⿻abc`
becomes unwieldy for three or more.

### 5.2 Grammar

```ebnf
(* Group expression *)
GRP_EXPR    ::= GRP_OPEN EXPR ( EXPR )+ GRP_CLOSE
GRP_OPEN    ::= '⟦' | '[['
GRP_CLOSE   ::= '⟧' | ']]'
EXPR        ::= CJK_CHAR | IDS_EXPR | GRP_EXPR | GRID_EXPR | '(' EXPR ')'
```

### 5.3 Semantics

All grouped elements occupy the same bounding box. Drawing order
follows argument order (first element drawn first, last on top).

Minimum 2 elements required (same as CSDL-ASCII GRP).

### 5.4 Examples

| CSDL-ASCII | CSDL-U | Notes |
|------------|--------|-------|
| `GRP(a, b)` | `⟦ab⟧` | Two elements (equiv. to OVR) |
| `GRP(a, b, c)` | `⟦abc⟧` | Three overlaid |
| `GRP(a, b, c, d)` | `⟦abcd⟧` | Four overlaid |
| `OVR(十, 口)` | `⿻十口` | Standard IDS overlay |

### 5.5 GRP vs OVR

`⟦ab⟧` is semantically equivalent to `⿻ab`. Authors SHOULD prefer
`⿻` for two elements (standard IDS) and use `⟦...⟧` for three or
more.

---

## 6. GRID Operator

### 6.1 Rationale

IDS has no 2x2 grid operator. CSDL's GRID operator is essential for
characters with four quadrants (e.g., 器-like structures with unequal
divisions).

### 6.2 Grammar

```ebnf
(* Grid expression *)
GRID_EXPR   ::= GRID_OP '(' EXPR PARAM_SEP EXPR PARAM_SEP EXPR PARAM_SEP EXPR
                ( PARAM_SEP SPLIT_VAL PARAM_SEP SPLIT_VAL )? ')'
GRID_OP     ::= '⊞' | '[+]'
PARAM_SEP   ::= '⹁' | ','
SPLIT_VAL   ::= UINT FRAC_SEP UINT
```

### 6.3 Semantics

GRID divides the parent box into a 2x2 matrix. Arguments in reading
order:
1. Top-left
2. Top-right
3. Bottom-left
4. Bottom-right

Optional split parameters:
- First split: horizontal division (left column / right column)
- Second split: vertical division (top row / bottom row)

Default splits: 6/6 horizontal, 6/6 vertical (equal quadrants).

### 6.4 Examples

| CSDL-ASCII | CSDL-U | Notes |
|------------|--------|-------|
| `GRID(口, 口, 口, 口)` | `⊞(口⹁口⹁口⹁口)` | Equal quadrants |
| `GRID(日, 月, 木, 心)` | `⊞(日⹁月⹁木⹁心)` | Custom elements |
| `GRID(日, 月, 木, 心, 5/7, 4/8)` | `⊞(日⹁月⹁木⹁心⹁5⁄7⹁4⁄8)` | Unequal splits |

### 6.5 GRID vs Nested LR/TB

GRID provides explicit 2x2 semantics. The equivalent nested expression:

```
# CSDL-ASCII
TB(LR(a, b), LR(c, d))

# CSDL-U (no GRID)
⿱⿰ab⿰cd
```

GRID is preferred when:
- Independent horizontal and vertical splits are needed
- The 2x2 structure should be explicit in the source
- Tooling benefits from recognizing the grid pattern

---

## 7. SUR (Surround) Extended Parameters

### 7.1 Rationale

Standard IDS surround operators (`⿴⿵⿶⿷⿸⿹⿺`) encode side but not
inset distance. CSDL's SUR operator accepts an optional inset parameter.

### 7.2 Grammar

```ebnf
(* Surround with inset annotation *)
SUR_INSET   ::= RATIO_DELIM UINT
RATIO_DELIM ::= '∶' | ':'
UINT        ::= [0-9]+   (* range: 0-6 *)
```

### 7.3 Semantics

The inset annotation specifies how many grid units the inner component
is inset from the covered sides. Default inset is 2.

### 7.4 Examples

| CSDL-ASCII | CSDL-U | Notes |
|------------|--------|-------|
| `SUR(囗, 王, full)` | `⿴囗王` | Default inset (2) |
| `SUR(囗, 王, full, 1)` | `⿴囗王∶1` | Tight fit |
| `SUR(囗, 王, full, 3)` | `⿴囗王∶3` | Loose fit |
| `SUR(广, 木, tl, 2)` | `⿸广木∶2` | Explicit default |
| `SUR(广, 木, tl, 3)` | `⿸广木∶3` | More padding |

### 7.5 Side Selection

The side is implicit in the IDS character choice:

| CSDL Side | IDS Character |
|-----------|---------------|
| `full` | `⿴` |
| `top` | `⿵` |
| `bot` | `⿶` |
| `left` | `⿷` |
| `tl` | `⿸` |
| `tr` | `⿹` |
| `bl` | `⿺` |

Note: CSDL-ASCII's `right` and `br` sides have no IDS equivalents.
Characters requiring these sides cannot be expressed in CSDL-U
without information loss. See Section 9 for mitigation strategies.

---

## 8. Combined Examples

### 8.1 Complex Character

CSDL-ASCII:
```
道 dao4 = SUR(辶, LR(首, sh(口, dx=1, dy=0), 7/5), bl, 2)
```

CSDL-U:
```
道 = ⿺辶(⿰首(口⊛sh(dx=1⹁dy=0))∶7⁄5)∶2
```

Breakdown:
- `⿺` = SUR with bl side
- `辶` = outer component
- `(⿰首(口⊛sh(dx=1⹁dy=0))∶7⁄5)` = inner component
  - `⿰` = LR
  - `首` = left child
  - `口⊛sh(dx=1⹁dy=0)` = right child, shifted
  - `∶7⁄5` = 7:5 split
- `∶2` = inset 2

### 8.2 Grid with Transforms

CSDL-ASCII:
```
GRID(sc(口, sx=10, sy=10), 口, 口, sc(口, sx=10, sy=10), 5/7, 5/7)
```

CSDL-U:
```
⊞(口⊛sc(sx=10⹁sy=10)⹁口⹁口⹁口⊛sc(sx=10⹁sy=10)⹁5⁄7⹁5⁄7)
```

### 8.3 Deep Nesting

CSDL-ASCII:
```
TB(LR(a, b, 4/8), LR3(c, d, e, 3/5/4), 5/7)
```

CSDL-U:
```
⿱(⿰ab∶4⁄8)(⿲cde∶3⁄5⁄4)∶5⁄7
```

---

## 9. Limitations and Mitigations

### 9.1 Features Without IDS Equivalent

| Feature | CSDL-ASCII | CSDL-U Mitigation |
|---------|------------|-------------------|
| `right` side | `SUR(a, b, right)` | Use `⿹` with note |
| `br` side | `SUR(a, b, br)` | No equivalent; round-trip loss |
| Strokes | `S(heng ...)` | Same syntax in both profiles |

### 9.2 Information Preservation

For lossless round-tripping of characters using `right` or `br` surround:

1. **Preferred:** Use CSDL-ASCII for these characters
2. **Alternative:** Extend IDS with private-use annotation:
   ```
   ⿹ab⊛side(right)
   ```
   This is non-standard and implementations MAY reject it.

### 9.3 Stroke-Level Definitions

Both CSDL-ASCII and CSDL-U use the same `S()` syntax for stroke
invocations. Stroke-level components cannot be expressed in pure
IDS notation; they require the full `@comp` block form regardless
of syntax profile.

---

## 10. EBNF Summary

```ebnf
(* === Lexical === *)
UINT        ::= [0-9]+
TPARAM      ::= '-'? UINT   (* range: -12 to 24 *)
CJK_CHAR    ::= (* per CSDL spec §6.2 *)

(* === Delimiters (canonical | ASCII fallback) === *)
RATIO_DELIM ::= '∶' | ':'
FRAC_SEP    ::= '⁄' | '/'
XFORM_DELIM ::= '⊛' | '@'
PARAM_SEP   ::= '⹁' | ','
GRP_OPEN    ::= '⟦' | '[['
GRP_CLOSE   ::= '⟧' | ']]'
GRID_OP     ::= '⊞' | '[+]'

(* === IDS Operators (Unicode Standard) === *)
IDS_OP_2    ::= '⿰' | '⿱' | '⿴' | '⿵' | '⿶' | '⿷' | '⿸' | '⿹' | '⿺' | '⿻'
IDS_OP_3    ::= '⿲' | '⿳'

(* === Splits === *)
SPLIT_2     ::= UINT FRAC_SEP UINT
SPLIT_3     ::= UINT FRAC_SEP UINT FRAC_SEP UINT
SPLIT_ANN   ::= RATIO_DELIM ( SPLIT_2 | SPLIT_3 )

(* === Transforms === *)
XFORM_OP    ::= 'sc' | 'sh' | 'sk'
PARAM_NAME  ::= 'sx' | 'sy' | 'dx' | 'dy' | 'kx' | 'ky'
PARAM_PAIR  ::= PARAM_NAME '=' TPARAM
XFORM_PARAMS::= PARAM_PAIR ( PARAM_SEP PARAM_PAIR )*
XFORM_ANN   ::= XFORM_DELIM XFORM_OP '(' XFORM_PARAMS ')'

(* === SUR Inset === *)
SUR_INSET   ::= RATIO_DELIM UINT   (* range: 0-6 *)

(* === Expressions === *)
ATOM        ::= CJK_CHAR | '(' EXPR ')'
IDS_EXPR_2  ::= IDS_OP_2 EXPR EXPR SPLIT_ANN? SUR_INSET?
IDS_EXPR_3  ::= IDS_OP_3 EXPR EXPR EXPR SPLIT_ANN?
GRP_EXPR    ::= GRP_OPEN EXPR EXPR+ GRP_CLOSE
GRID_ARGS   ::= EXPR PARAM_SEP EXPR PARAM_SEP EXPR PARAM_SEP EXPR
                ( PARAM_SEP SPLIT_2 PARAM_SEP SPLIT_2 )?
GRID_EXPR   ::= GRID_OP '(' GRID_ARGS ')'

BASE_EXPR   ::= ATOM | IDS_EXPR_2 | IDS_EXPR_3 | GRP_EXPR | GRID_EXPR
EXPR        ::= BASE_EXPR XFORM_ANN*

(* === Character Definition === *)
PINYIN_NAME ::= (* per CSDL spec §6.2 *)
CHAR_DEF    ::= CJK_CHAR ( ' ' PINYIN_NAME )? ' = ' EXPR
```

---

## 11. Design Rationale

### 11.1 Why Unicode Delimiters?

1. **Collision avoidance:** ASCII `:` could appear in URLs, `@` in
   email addresses, `/` in paths. Unicode delimiters (`∶`, `⊛`, `⁄`)
   are unambiguous in CJK text contexts.

2. **Visual clarity:** Unicode mathematical symbols stand out in
   mixed CJK/Latin text, making annotations visually distinct from
   component references.

3. **Standardization path:** If CSDL-U were proposed for Unicode
   standardization, novel delimiters from established mathematical
   blocks are more defensible than overloaded ASCII punctuation.

### 11.2 Why ASCII Fallbacks?

1. **Input practicality:** Many keyboards lack easy input for `∶`
   or `⊛`. Authors should not be blocked by input method limitations.

2. **Legacy compatibility:** Existing tools, editors, and databases
   may not handle all Unicode characters gracefully. ASCII fallback
   ensures CSDL-U can be authored anywhere.

3. **Spec hint alignment:** The CSDL 1.0 specification already hints
   at `:4/8` and `@sc(8,8)` syntax. Supporting these as fallbacks
   maintains compatibility with early implementations.

### 11.3 Why Postfix Transforms?

CSDL-ASCII uses prefix notation: `sc(expr, sx=8, sy=8)`. CSDL-U uses
postfix: `expr⊛sc(sx=8⹁sy=8)`.

Rationale:
1. **IDS compatibility:** IDS is prefix notation for operators but
   has no transforms. Adding postfix transforms keeps operators
   prefix and modifiers postfix, creating a consistent model.

2. **Readability:** `⿰日月∶4⁄8` reads as "LR composition of 日 and 月
   with 4:8 split" - the annotation follows the thing it modifies.

3. **Chaining:** Multiple transforms read left-to-right in application
   order: `a⊛sc(...)⊛sh(...)` applies scale then shift.

### 11.4 Why Mathematical Brackets for GRP?

`⟦` and `⟧` (U+27E6/U+27E7) are:
- Visually distinct from CJK brackets (「」, 『』, 【】)
- Not used in IDS or existing CJK encoding standards
- Semantically appropriate (mathematical grouping)
- Well-supported in modern fonts

### 11.5 Why Squared Plus for GRID?

`⊞` (U+229E) visually suggests a four-quadrant division. It is:
- Not used in IDS
- Semantically evocative (plus sign = cross = four quarters)
- Available in most mathematical fonts
- Distinct from CJK characters

---

## 12. Implementation Notes

### 12.1 Parsing Strategy

1. **Tokenize:** Identify IDS operators, delimiters, CJK characters,
   and ASCII sequences.

2. **Parse IDS:** Use standard IDS parsing (prefix, fixed arity).

3. **Attach annotations:** After parsing an IDS expression or atom,
   check for trailing annotations (`∶`, `⊛`).

4. **Validate:** Ensure splits match operator arity, transform
   parameters are in range, insets are 0-6.

### 12.2 Round-Trip Conversion

CSDL-ASCII to CSDL-U:
1. Replace layout operators with IDS characters
2. Move split parameters to postfix annotation
3. Convert transform prefix to postfix
4. Convert GRP to `⟦...⟧`
5. Convert GRID to `⊞(...)`

CSDL-U to CSDL-ASCII:
1. Replace IDS characters with layout operators
2. Move split annotations to operator parameters
3. Convert transform postfix to prefix
4. Convert `⟦...⟧` to GRP
5. Convert `⊞(...)` to GRID

### 12.3 Error Handling

- Split on non-splittable operator: Error
- Split arity mismatch: Error (e.g., 3-way split on binary operator)
- Transform parameter out of range: Error
- Inset on non-SUR operator: Error
- GRP with fewer than 2 elements: Error
- GRID with wrong argument count: Error

---

## 13. Future Considerations

### 13.1 Unicode Proposal

If CSDL gains adoption, a Unicode proposal could request:
- Dedicated IDS extension characters for GRP and GRID
- Annotation mechanism standardization

Until then, CSDL-U uses characters from existing blocks.

### 13.2 Extended Surround Sides

`right` and `br` surround sides have no IDS equivalent. Options:
1. Accept information loss for these rare cases
2. Propose new IDS characters (U+2FFC, U+2FFD are reserved)
3. Use private-use annotation syntax

### 13.3 Stroke Extensions

Stroke-level syntax (`S(...)`) is shared between profiles. A future
extension might define Unicode-native stroke notation, but this is
out of scope for CSDL 1.0.

---

## 14. References

- CSDL Specification v1.0, Sections 1.5, 6, 8, 9, Appendix A
- Unicode Standard, Chapter 18 (Han)
- Unicode Technical Report #45 (IDS)
- BCP 47 (Language Tags)
