# CSDL-U Formal Grammar

This document specifies the complete formal grammar for the CSDL-U
syntax profile. CSDL-U uses Unicode Ideographic Description Characters
(IDS operators) instead of ASCII layout operator names, enabling a
more compact and Unicode-native representation.

## 1. Overview

CSDL-U and CSDL-ASCII are mechanically interconvertible and
semantically equivalent. The key differences are:

| Feature | CSDL-ASCII | CSDL-U |
|---------|------------|--------|
| Layout operators | ASCII names (`LR`, `TB`, etc.) | IDS characters (U+2FF0-U+2FFB) |
| Delimiters | Parentheses and commas | None (fixed-arity prefix notation) |
| Pinyin aliases | Supported | Not supported |
| Component references | CJK or pinyin | CJK only |
| Split ratios | Inline parameter | Annotation suffix (`:ratio`) |
| Transforms | Wrapper functions | Annotation suffix (`@transform`) |

### 1.1 IDS Operator Mapping

| IDS | Code Point | Arity | CSDL-ASCII Equivalent |
|-----|------------|-------|----------------------|
| `⿰` | U+2FF0 | 2 | `LR(a, b)` |
| `⿱` | U+2FF1 | 2 | `TB(a, b)` |
| `⿲` | U+2FF2 | 3 | `LR3(a, b, c)` |
| `⿳` | U+2FF3 | 3 | `TB3(a, b, c)` |
| `⿴` | U+2FF4 | 2 | `SUR(a, b, full)` |
| `⿵` | U+2FF5 | 2 | `SUR(a, b, top)` |
| `⿶` | U+2FF6 | 2 | `SUR(a, b, bot)` |
| `⿷` | U+2FF7 | 2 | `SUR(a, b, left)` |
| `⿸` | U+2FF8 | 2 | `SUR(a, b, tl)` |
| `⿹` | U+2FF9 | 2 | `SUR(a, b, tr)` |
| `⿺` | U+2FFA | 2 | `SUR(a, b, bl)` |
| `⿻` | U+2FFB | 2 | `OVR(a, b)` |

**Note:** CSDL-ASCII operators `GRP`, `GRID`, and surround sides
`right` and `br` have no IDS equivalents. CSDL-U cannot express these
directly; files requiring them must use CSDL-ASCII or embedded
ASCII-syntax blocks.

---

## 2. Notation

This grammar uses W3C EBNF notation with the same conventions as the
CSDL-ASCII grammar (see csdl-spec.md Section 6.1):

- `'literal'` denotes a terminal string.
- `#xN` denotes a Unicode code point.
- `/* ... */` are grammar comments.
- `[a-z]` denotes a character range (POSIX-style).
- `[^#xN]` denotes any scalar value except those listed.

---

## 3. Lexical Productions

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

(* Unicode code point label *)
CODEPOINT   ::= 'U+' [0-9A-Fa-f]{4,6}

(* CJK character ranges (Unicode 16.0) *)
CJK_CHAR    ::= [#x3400-#x9FFF]
              | [#xF900-#xFAFF]
              | [#x20000-#x2FA1F]
              | [#x30000-#x3134F]
              | [#x31350-#x323AF]

(* Variant tag for positional variants *)
VARIANT_TAG ::= '.' [a-z] [a-z0-9]*

(* Component name: CJK character with optional variant tags
   NOTE: CSDL-U does not support pinyin-only names *)
COMP_NAME_U ::= CJK_CHAR VARIANT_TAG*
```

---

## 4. IDS Operator Productions

```ebnf
(* IDS operators by arity *)
IDS_OP_2    ::= #x2FF0   (* ⿰ Left-Right *)
              | #x2FF1   (* ⿱ Top-Bottom *)
              | #x2FF4   (* ⿴ Full Surround *)
              | #x2FF5   (* ⿵ Surround from Above *)
              | #x2FF6   (* ⿶ Surround from Below *)
              | #x2FF7   (* ⿷ Surround from Left *)
              | #x2FF8   (* ⿸ Surround Upper-Left *)
              | #x2FF9   (* ⿹ Surround Upper-Right *)
              | #x2FFA   (* ⿺ Surround Lower-Left *)
              | #x2FFB   (* ⿻ Overlay *)

IDS_OP_3    ::= #x2FF2   (* ⿲ Left-Middle-Right *)
              | #x2FF3   (* ⿳ Top-Middle-Bottom *)

IDS_OP      ::= IDS_OP_2 | IDS_OP_3
```

---

## 5. Annotation Productions

Annotations extend IDS expressions with CSDL-specific features not
expressible in standard IDS. Annotations attach to the preceding
element.

```ebnf
(* Split ratio annotation - attaches to IDS operator expressions *)
SPLIT_2     ::= UINT '/' UINT
SPLIT_3     ::= UINT '/' UINT '/' UINT
SPLIT_ANNOT ::= ':' ( SPLIT_2 | SPLIT_3 )

(* Transform parameter *)
TPARAM      ::= INT   /* constrained: -12 <= value <= 24 */

(* Transform annotations - attach to component or expression *)
SC_ANNOT    ::= '@sc(' TPARAM ',' TPARAM ')'
SH_ANNOT    ::= '@sh(' TPARAM ',' TPARAM ')'
SK_ANNOT    ::= '@sk(' TPARAM ',' TPARAM ')'
XFORM_ANNOT ::= SC_ANNOT | SH_ANNOT | SK_ANNOT

(* Combined annotation - split must precede transform if both present *)
ANNOTATION  ::= SPLIT_ANNOT? XFORM_ANNOT?
```

### 5.1 Annotation Attachment Rules

1. **Split annotations** (`:ratio`) attach to the immediately
   preceding IDS operator expression. The ratio specifies how to
   divide the parent box among children.

2. **Transform annotations** (`@transform`) attach to the immediately
   preceding atom (component reference or parenthesized expression).

3. When both appear, split precedes transform: `⿰木木:4/8@sc(10,10)`

4. Annotations bind tightly. In `⿰木木:4/8`, the `:4/8` annotates the
   entire `⿰木木` expression, not just `木`.

---

## 6. Expression Productions

CSDL-U expressions use prefix notation with fixed arity, eliminating
the need for parentheses and commas.

```ebnf
(* Atomic expressions *)
ATOM        ::= COMP_NAME_U XFORM_ANNOT?
              | '(' IDS_EXPR ')' XFORM_ANNOT?

(* IDS expressions - recursive prefix notation *)
IDS_EXPR_2  ::= IDS_OP_2 ATOM ATOM SPLIT_ANNOT?
IDS_EXPR_3  ::= IDS_OP_3 ATOM ATOM ATOM SPLIT_ANNOT?
IDS_EXPR    ::= IDS_EXPR_2 | IDS_EXPR_3 | ATOM

(* Top-level expression *)
EXPR_U      ::= IDS_EXPR
```

### 6.1 Recursive Structure

IDS expressions nest naturally through their operands. Each operand
position can be:
- A bare component name (`木`)
- A component with transform (`木@sc(8,8)`)
- A nested IDS expression (the next IDS operator begins a new subtree)

The fixed arity of each operator makes parsing unambiguous:

```
⿱木⿰木木     parses as: ⿱(木, ⿰(木, 木))
⿲木木木       parses as: ⿲(木, 木, 木)
⿰⿱木木⿱木木 parses as: ⿰(⿱(木, 木), ⿱(木, 木))
```

---

## 7. Stroke Productions

Stroke definitions use the same syntax in both CSDL-ASCII and CSDL-U.
The `S()` function syntax is retained for stroke-level component
definitions.

```ebnf
(* Coordinate pair *)
COORD       ::= '[' UINT ',' UINT ']'

(* Grid override *)
GRID_SPEC   ::= '/24' | '/12'

(* Stroke width *)
WIDTH       ::= '0' | '1' | '2'

(* Standard stroke name from closed registry *)
STD_STROKE  ::= [a-z]+ ( '-' [a-z]+ )*

(* Extension stroke name *)
EXT_STROKE  ::= 'x-' [a-z]+ ( '-' [a-z]+ )*

STROKE_NAME ::= STD_STROKE | EXT_STROKE

(* Stroke invocation *)
STROKE_EXPR ::= 'S(' STROKE_NAME WS COORD ( WS COORD )+ WS WIDTH ')'

(* Stroke identifier for build order *)
STROKE_ID   ::= [a-z] [a-z0-9]*

(* Stroke definition line *)
STROKE_DEF  ::= STROKE_ID WS '=' WS STROKE_EXPR
```

---

## 8. Definition Productions

```ebnf
(* Metadata fields - same as CSDL-ASCII *)
META_RAD    ::= 'rad:' WS? UINT
META_SC     ::= 'sc:' WS? UINT
META_FREQ   ::= 'freq:' WS? UINT
META_ORTHO  ::= 'ortho:' WS? ORTHO_LIST
META_EXT    ::= 'x-' LETTER+ ':' WS? [^#x0A#x0D]+
METADATA    ::= META_RAD | META_SC | META_FREQ | META_ORTHO | META_EXT

(* Orthography tags *)
BCP47_TAG   ::= LETTER LETTER LETTER LETTER
CSDL_XTAG   ::= 'x-' LETTER+
ORTHO_TAG   ::= BCP47_TAG | CSDL_XTAG
ORTHO_LIST  ::= ORTHO_TAG ( ',' ORTHO_TAG )*

(* Build order *)
BUILD_STROKES ::= 'build:' WS? STROKE_ID ( WS STROKE_ID )*
BUILD_EXPR    ::= 'build:' WS? 'from_expr'
BUILD_LINE    ::= BUILD_STROKES | BUILD_EXPR

(* Closing stroke marker *)
CLOSE_LINE    ::= 'close:' WS? STROKE_ID

(* Character inline form - CSDL-U style
   NOTE: No pinyin name required; character identity from CJK_CHAR *)
CHAR_INLINE_U ::= CJK_CHAR WS '=' WS EXPR_U ( WS METADATA )* NL

(* Character block forms use same syntax as CSDL-ASCII *)
CHAR_STROKE_BODY ::= ( BUILD_STROKES NL )?
                     ( CLOSE_LINE NL )?
                     ( STROKE_DEF NL )+
CHAR_EXPR_BODY   ::= BUILD_EXPR NL
                     EXPR_U NL

CHAR_BLOCK_U ::= '@char' WS CJK_CHAR NL
                 ( CHAR_STROKE_BODY | CHAR_EXPR_BODY )
                 ( METADATA NL )*
                 '@end' NL

(* Component block forms *)
COMP_STROKE_BODY ::= ( BUILD_STROKES NL )?
                     ( CLOSE_LINE NL )?
                     ( STROKE_DEF NL )+
COMP_EXPR_BODY   ::= BUILD_EXPR NL
                     EXPR_U NL

COMP_BLOCK_U ::= '@comp' WS COMP_NAME_U ( WS GRID_SPEC )? NL
                 ( COMP_STROKE_BODY | COMP_EXPR_BODY )
                 ( METADATA NL )*
                 '@end' NL
```

---

## 9. File Productions

```ebnf
(* Format declaration *)
FORMAT_DECL  ::= '@csdl' WS DIGIT+ '.' DIGIT+ NL

(* File-level orthography declaration *)
ORTHO_DECL  ::= '@ortho' WS ORTHO_TAG NL

(* Top-level definition *)
DEFINITION_U ::= COMP_BLOCK_U | CHAR_INLINE_U | CHAR_BLOCK_U

(* Complete file
   NOTE: CSDL-U files do not support @alias (no pinyin names) *)
CSDL_U_FILE ::= FORMAT_DECL
                ORTHO_DECL?
                ( DEFINITION_U | COMMENT | BLANK_LINE )*
```

---

## 10. Parsing Algorithm

### 10.1 Recursive Descent Parser

CSDL-U's prefix notation with fixed-arity operators is naturally
parsed by recursive descent. The key insight is that each IDS operator
declares exactly how many operands follow.

```
function parseExpr():
    if peek() is IDS_OP_2:
        op = consume()
        left = parseExpr()
        right = parseExpr()
        annot = parseSplitAnnot()  // optional
        return IdsExpr2(op, left, right, annot)

    else if peek() is IDS_OP_3:
        op = consume()
        a = parseExpr()
        b = parseExpr()
        c = parseExpr()
        annot = parseSplitAnnot()  // optional
        return IdsExpr3(op, a, b, c, annot)

    else if peek() is '(':
        consume('(')
        inner = parseExpr()
        consume(')')
        xform = parseXformAnnot()  // optional
        return Grouped(inner, xform)

    else if peek() is CJK_CHAR:
        name = parseCompName()
        xform = parseXformAnnot()  // optional
        return CompRef(name, xform)

    else:
        error("Expected IDS operator or component")
```

### 10.2 Ambiguity Resolution

CSDL-U has no parsing ambiguities due to:

1. **Fixed arity**: Each IDS operator has a known operand count.
   The parser always knows how many sub-expressions to consume.

2. **Distinct token classes**: IDS operators (U+2FF0-U+2FFB), CJK
   characters, and annotation markers (`:`, `@`) form disjoint sets.

3. **Greedy annotation binding**: Annotations bind to the immediately
   preceding element. There is no ambiguity about what `:4/8` or
   `@sc(8,8)` modifies.

### 10.3 Lookahead Requirements

CSDL-U requires only single-character lookahead:

| Lookahead | Interpretation |
|-----------|----------------|
| IDS operator (U+2FF0-U+2FFB) | Begin new IDS expression |
| CJK character (not IDS) | Component reference |
| `:` | Split annotation follows |
| `@` | Transform annotation follows |
| `(` | Grouped sub-expression |
| `)` | End of grouped expression |

### 10.4 Handling Nested Expressions

Consider `⿱木⿰木木` ("forest" structure):

```
Position 0: ⿱ (IDS_OP_2, expects 2 operands)
  Operand 1:
    Position 1: 木 (CJK_CHAR, complete atom)
  Operand 2:
    Position 2: ⿰ (IDS_OP_2, expects 2 operands)
      Operand 1:
        Position 3: 木 (CJK_CHAR, complete atom)
      Operand 2:
        Position 4: 木 (CJK_CHAR, complete atom)
    (⿰ complete)
  (⿱ complete)
```

The parse tree is:
```
TB
├── 木
└── LR
    ├── 木
    └── 木
```

---

## 11. Examples

### 11.1 Valid Syntax

```
# Simple binary composition
明 = ⿰日月

# Ternary composition
謝 = ⿰言⿱身寸

# With split ratio
林 = ⿰木木:6/6

# With transform
字 = ⿱宀子@sc(10,10)

# Nested with annotations
街 = ⿲彳⿱土土亍:3/6/3

# Multiple levels of nesting
器 = ⿳⿰口口犬⿰口口

# Transform on inner component
微 = ⿰彳⿳山⿱一几攵@sh(0,-1)

# Grouped subexpression with transform
複 = ⿰⿱日⿰日日@sc(8,8)夊
```

### 11.2 Invalid Syntax

```
# INVALID: Pinyin not allowed in CSDL-U
ming2 = ⿰ri4 yue4

# INVALID: Wrong operand count for ⿰ (expects 2, got 3)
⿰木木木

# INVALID: Wrong operand count for ⿲ (expects 3, got 2)
⿲木木

# INVALID: Split annotation on atom (must be on IDS expression)
明 = ⿰日月:4/8@sc(8,8)  # OK
明 = ⿰日:4/8月          # INVALID - :4/8 on component

# INVALID: Transform annotation on IDS operator (must be on atom)
明 = ⿰@sc(8,8)日月      # INVALID

# INVALID: GRP operator (no IDS equivalent)
# Must use CSDL-ASCII for this pattern
```

### 11.3 Equivalent Forms (CSDL-ASCII / CSDL-U)

| CSDL-ASCII | CSDL-U |
|------------|--------|
| `LR(日, 月)` | `⿰日月` |
| `TB(木, LR(木, 木))` | `⿱木⿰木木` |
| `LR(日, 月, 4/8)` | `⿰日月:4/8` |
| `sc(字, sx=10, sy=10)` | `字@sc(10,10)` |
| `LR(sc(日, sx=8, sy=8), 月)` | `⿰日@sc(8,8)月` |
| `SUR(門, 日, full)` | `⿴門日` |
| `SUR(广, 黃, tl)` | `⿸广黃` |

---

## 12. Component and Character Blocks

Block-form definitions in CSDL-U use the same structure as CSDL-ASCII,
with two key differences:

1. Component names use only CJK characters (no pinyin)
2. Expression bodies use IDS syntax

### 12.1 Component Block Example

```
@comp 口
build: h v h2 v2
h  = S(heng [0,4] [12,4] 1)
v  = S(shu [0,4] [0,8] 1)
h2 = S(heng [0,8] [12,8] 1)
v2 = S(shu [12,4] [12,8] 1)
@end
```

### 12.2 Character Block with Expression

```
@char 明
build: from_expr
⿰日月
rad: 72
sc: 8
@end
```

### 12.3 Character Block with Strokes

```
@char 一
build: h
h = S(heng [0,6] [12,6] 2)
rad: 1
sc: 1
@end
```

---

## 13. Semantic Constraints

All semantic constraints from CSDL-ASCII Section 6.9 apply to CSDL-U,
with the following profile-specific constraints:

1. **No pinyin names**: Component references MUST be CJK characters.
   The `PINYIN_NAME` and `PINYIN_SYLL` productions are not part of
   CSDL-U.

2. **No aliases**: The `@alias` directive is not supported in CSDL-U
   files, as it exists to map pinyin names to CJK characters.

3. **Split arity match**: A `:SPLIT_2` annotation MUST only appear
   on a binary IDS expression (`IDS_OP_2`). A `:SPLIT_3` annotation
   MUST only appear on a ternary IDS expression (`IDS_OP_3`).

4. **No GRP or GRID**: Expressions requiring `GRP` or `GRID` operators
   cannot be represented in pure CSDL-U. Such definitions MUST use
   CSDL-ASCII syntax.

5. **No right/br surround**: The surround sides `right` and `br` have
   no IDS equivalents. Characters requiring these MUST use CSDL-ASCII.

6. **Transform parameter bounds**: All transform annotation parameters
   MUST be in the range -12 to 24 inclusive.

7. **Split values positive**: All values in split annotations MUST be
   positive integers.

---

## 14. Differences from CSDL-ASCII

| Aspect | CSDL-ASCII | CSDL-U |
|--------|------------|--------|
| Layout operators | ASCII keywords | IDS characters |
| Operator syntax | `OP(arg, arg)` | `⿰argarg` |
| Delimiters | Required (parens, commas) | None |
| Pinyin names | Supported | Not supported |
| Aliases | `@alias` directive | Not supported |
| Split ratios | Inline: `LR(a, b, 4/8)` | Suffix: `⿰ab:4/8` |
| Transforms | Wrapper: `sc(a, sx=8, sy=8)` | Suffix: `a@sc(8,8)` |
| GRP operator | Supported | Not available |
| GRID operator | Supported | Not available |
| Surround sides | All 9 sides | 7 sides (no right, br) |
| Stroke syntax | `S(...)` | `S(...)` (same) |
| Metadata | Same | Same |
| Comments | `#` | `#` (same) |

---

## 15. References

- CSDL Specification, Section 6: Expression Grammar (CSDL-ASCII)
- CSDL Specification, Section 1.5: Syntax Profiles
- CSDL Specification, Appendix A: IDS Operator Mapping
- Unicode Standard, Chapter 18: East Asian Scripts (IDS)
- ISO 10646: Ideographic Description Characters (U+2FF0-U+2FFB)
