# CSDL Unicode Adoption Strategy

**Document Status:** Strategic Planning
**Version:** 1.0
**Date:** 2026-06-21
**Author:** Mark Atwood

---

## Executive Summary

This document outlines a strategy for positioning CSDL (CJK Stroke Description
Language) as a candidate for Unicode standardization. CSDL occupies a unique
position: it extends Unicode's existing Ideographic Description Sequences (IDS)
with geometric precision, stroke-level detail, and transform operations while
remaining mechanically interconvertible with pure IDS. The CSDL-U profile uses
Unicode's own Ideographic Description Characters (U+2FF0-U+2FFB) as layout
operators, making CSDL a natural extension rather than a competing approach.

The recommended path is to pursue Unicode Technical Standard (UTS) status,
which allows CSDL to maintain its independent specification while gaining
formal recognition within the Unicode ecosystem.

---

## 1. What CSDL Adds Beyond IDS

Unicode's Ideographic Description Sequences (IDS) provide symbolic
decomposition of CJK characters using 12 composition operators (U+2FF0-U+2FFB).
IDS answers the question "what parts make up this character?" but does not
address geometry, proportions, strokes, or rendering parameters.

CSDL fills this gap with four key additions:

### 1.1 Geometric Coordinates

CSDL introduces a 12x12 grid coordinate system that specifies where elements
are placed within a character's bounding box. This enables:

- **Precise split ratios**: `LR(a, b, 4/8)` vs IDS's unspecified `⿰ab`
- **Coordinate-based stroke placement**: `S(heng [2,4] [10,4] 1)`
- **Deterministic layout**: Same expression always yields same geometry

IDS says "left-right composition"; CSDL says "left-right composition with
the left component taking 4 units and the right component taking 8 units."

### 1.2 Stroke Registry

CSDL defines 38 named stroke primitives:

| Category | Count | Examples |
|----------|-------|----------|
| Base strokes | 12 | heng, shu, pie, na, dian, ti, gou, wan, zhe, xie, wo, quan |
| Single-fold compounds | 12 | heng-zhe, shu-gou, pie-dian |
| Double-fold compounds | 8 | heng-zhe-gou, shu-wan-gou |
| Triple-fold compounds | 5 | heng-zhe-wan-gou |
| Quadruple-fold compounds | 1 | heng-zhe-zhe-zhe-gou |

The stroke names use pinyin (romanized Chinese), matching calligraphic
tradition. Each stroke is invoked with coordinates: `S(heng-zhe [3,2] [9,2]
[9,10] 1)` specifies a horizontal-turn stroke at specific grid points.

This closed registry (no new strokes without major version bump) ensures
interoperability and prevents dialect fragmentation.

### 1.3 Transform Operators

Three geometric transforms enable adjustment of components:

| Operator | Function | Example |
|----------|----------|---------|
| `sc(x, sx, sy)` | Scale | `sc(mouth, sx=8, sy=8)` shrinks to 2/3 |
| `sh(x, dx, dy)` | Shift | `sh(mouth, dx=2, dy=1)` translates |
| `sk(x, kx, ky)` | Skew | `sk(tree, kx=1, ky=0)` shears |

Transforms compose inside-out, providing a small but complete set of 2D
affine operations for positioning adjustments.

### 1.4 Orthography Tags

CSDL uses BCP 47 script subtags to annotate writing traditions:

- `Hant` - Traditional Chinese
- `Hans` - Simplified Chinese
- `Jpan` - Japanese Kanji
- `Kore` - Korean Hanja
- Extension tags: `x-HantHK`, `x-HantTW`, `x-Kyuj`, `x-Shin`

This allows a single CSDL database to contain variant definitions for the
same code point across orthographies, with renderer-based selection.

### 1.5 Why These Extensions Matter

**Font Engineering**: Font developers can use CSDL as an intermediate
representation that preserves component structure through the compilation
pipeline. Currently, OpenType compilation destroys all semantic structure.

**Education**: Language learning applications can present character
construction as a step-by-step process with explicit coordinates, not
just "this character contains these parts."

**Accessibility**: Screen readers and assistive technologies could
describe characters structurally ("sun on the left, moon on the right,
split 50-50") rather than by name alone.

**Character Recognition**: ML systems can use structural decomposition
as training signal or validation, improving OCR and handwriting recognition.

**Variant Analysis**: Systematic comparison of orthographic variants
becomes computable when definitions specify exact geometries.

---

## 2. Relationship to Existing Unicode

### 2.1 Ideographic Description Sequences (U+2FF0-U+2FFB)

CSDL-U, the Unicode-native profile of CSDL, uses the 12 Ideographic
Description Characters directly as layout operators:

| IDS Character | Code Point | CSDL-ASCII | CSDL-U |
|---------------|------------|------------|--------|
| ⿰ | U+2FF0 | `LR(a, b)` | `⿰ab` |
| ⿱ | U+2FF1 | `TB(a, b)` | `⿱ab` |
| ⿲ | U+2FF2 | `LR3(a, b, c)` | `⿲abc` |
| ⿳ | U+2FF3 | `TB3(a, b, c)` | `⿳abc` |
| ⿴ | U+2FF4 | `SUR(a, b, full)` | `⿴ab` |
| ⿵ | U+2FF5 | `SUR(a, b, top)` | `⿵ab` |
| ⿶ | U+2FF6 | `SUR(a, b, bot)` | `⿶ab` |
| ⿷ | U+2FF7 | `SUR(a, b, left)` | `⿷ab` |
| ⿸ | U+2FF8 | `SUR(a, b, tl)` | `⿸ab` |
| ⿹ | U+2FF9 | `SUR(a, b, tr)` | `⿹ab` |
| ⿺ | U+2FFA | `SUR(a, b, bl)` | `⿺ab` |
| ⿻ | U+2FFB | `OVR(a, b)` | `⿻ab` |

Any pure IDS expression is valid CSDL-U. CSDL-U is a **strict superset**:
it adds annotation syntax for split ratios (`⿰ab:4/8`) and transforms
(`a@sc(8,8)`) but never changes IDS semantics.

This relationship is critical: CSDL does not compete with IDS. It extends
IDS with optional geometric detail that implementations can ignore if
they only need topological decomposition.

### 2.2 Unihan Database (UAX #38)

The Unihan database currently provides:

- `kTotalStrokes` - Stroke count
- `kRSUnicode` - Radical-stroke index
- Various source mappings

A provisional `kIDS` property was planned for Unicode 17.0 (per L2/21-118R),
providing IDS decompositions for all ideographs. CSDL can:

1. **Import**: Convert `kIDS` values to CSDL expressions (trivial, since
   CSDL-U is an IDS superset)
2. **Export**: Strip CSDL to pure IDS for `kIDS` population
3. **Extend**: Provide optional `kCSDL` property with geometric detail

The import/export relationship means CSDL databases can be maintained in
parallel with Unihan, with mechanical synchronization.

### 2.3 CJK Strokes Block (U+31C0-U+31EF)

The CJK Strokes block contains 39 characters representing stroke shapes,
originally from HKSCS-2001. These are **stroke glyphs for display**, not
a stroke description grammar.

CSDL stroke names partially overlap:

| CSDL Stroke | Unicode | Code Point | Notes |
|-------------|---------|------------|-------|
| heng | CJK STROKE H | U+31D4 | Horizontal |
| shu | CJK STROKE S | U+31D5 | Vertical |
| pie | CJK STROKE P | U+31D0 | Left-falling |
| na | CJK STROKE N | U+31D8 | Right-falling |
| dian | CJK STROKE D | U+31D6 | Dot |

However, CSDL provides finer compound stroke granularity (26 compounds vs.
Unicode's stroke glyphs which are largely single strokes). A future
alignment could map CSDL compound strokes to Unicode character sequences
or propose additions to the CJK Strokes block.

### 2.4 Summary: Positioning

CSDL is positioned as:

- **Superset of IDS**: Any IDS is valid CSDL-U
- **Complement to Unihan**: Provides geometry IDS lacks
- **Extension mechanism for CJK Strokes**: Proposes naming/composition system

This is "inside the tent" positioning: CSDL builds on Unicode foundations
rather than proposing alternatives.

---

## 3. Standardization Path Options

Three paths are available for Unicode recognition:

### 3.1 Option A: Unicode Technical Standard (UTS)

**Description**: UTS documents are independent specifications that do not
form part of the Unicode Standard itself. Conformance to Unicode does not
require conformance to any UTS.

**Precedents**:
- UTS #10: Unicode Collation Algorithm
- UTS #39: Unicode Security Mechanisms
- UTS #46: Unicode IDNA Compatibility Processing
- UTS #51: Unicode Emoji

**Process**:
1. Submit specification to UTC as document (L2/XX-XXX)
2. Propose Draft Unicode Technical Standard status
3. Public review periods (typically 90 days)
4. Iterate based on feedback
5. Advance to UTS with UTC majority vote

**Pros**:
- Independent versioning (CSDL can evolve on its own schedule)
- Does not require changes to Unicode Standard proper
- Clear scope boundary (implementers know CSDL is optional)
- Fastest path to recognition

**Cons**:
- Lower "status" than UAX (not integral to Unicode Standard)
- May be perceived as less mandatory for adoption

**Recommendation**: This is the preferred path. CSDL's role as an optional
extension layer aligns perfectly with UTS scope.

### 3.2 Option B: Unicode Standard Annex (UAX)

**Description**: UAX documents form an integral part of the Unicode Standard.
Conformance to a Unicode version includes conformance to its annexes.

**Precedents**:
- UAX #15: Unicode Normalization Forms
- UAX #29: Unicode Text Segmentation
- UAX #38: Unicode Han Database (Unihan)
- UAX #44: Unicode Character Database

**Process**:
1. Submit as DUTR (Draft Unicode Technical Report)
2. Public review, iteration
3. Advance to UTR status
4. After maturity, propose elevation to UAX
5. Requires UTC supermajority for standard incorporation

**Pros**:
- Highest recognition level
- Implementers must address CSDL for full conformance
- Direct integration with Unihan (UAX #38)

**Cons**:
- Much longer timeline (3-5+ years typical)
- Requires proving CSDL is essential to Unicode conformance
- Tighter coupling to Unicode version schedule
- Higher bar for approval

**Assessment**: Premature. UAX requires demonstrated need and stability.
CSDL should prove itself as UTS first, then potentially elevate.

### 3.3 Option C: IRG Working Document

**Description**: Submit CSDL to the Ideographic Research Group (IRG) as a
working document for CJK character processing.

**Context**: The IRG is responsible for CJK Unified Ideographs extensions
and uses IDS extensively in its unification work. Per recent developments,
IRG now uses IDS to identify duplicates and unifiables.

**Process**:
1. Contact IRG convenor (currently Ken Lunde as of June 2024)
2. Submit as IRG document (IRG N-XXXX)
3. Present at IRG meeting (held ~2x annually)
4. Seek adoption as IRG-recommended tool

**Pros**:
- Direct access to CJK expert community
- IRG's IDS usage creates natural alignment
- Could become de facto standard for IRG work
- Pathway to UTC via IRG recommendation

**Cons**:
- IRG scope is character encoding, not rendering/description
- May be seen as out of scope for IRG mandate
- Does not provide formal Unicode standardization

**Assessment**: Complementary to Option A. Pursue IRG engagement for
expert community adoption while seeking UTS status through UTC.

### 3.4 Recommended Path

**Primary**: Pursue UTS status through UTC submission (Option A)
**Secondary**: Engage IRG for expert community adoption (Option C)
**Future**: Consider UAX elevation after 2-3 years of UTS stability

---

## 4. Engagement Strategy

### 4.1 Who to Contact

**UTC (Primary)**:
- Submit documents via unicode.org/reporting.html
- Anyone can submit proposals; membership not required
- Key contacts: UTC chair, script encoding working group

**IRG (Secondary)**:
- Convenor: Ken Lunde (as of June 2024)
- IRG liaison organizations include UTC, SAT Daizoko Text Database
- Contact via unicode.org/irg/

**Liaison Organizations**:
- W3C: For web platform alignment (CSS, SVG, fonts)
- IETF: For protocol considerations (BCP 47 alignment is good)
- OpenType: Microsoft Typography team (OpenType integration)

### 4.2 What to Prepare

**Reference Implementation**:
- [x] Level 1 parser (Python, ~670 lines) - complete
- [ ] Level 2 renderer (bounding box computation) - in progress
- [ ] Level 3 full renderer (stroke expansion) - planned
- [ ] Test suite with known-good outputs
- [ ] Web-based demo for interactive exploration

**Documentation**:
- [x] Normative specification (csdl-spec.md) - complete
- [x] Primer for humans (primer.md) - complete
- [ ] Implementation guide
- [ ] Migration guide (IDS to CSDL-U)

**Test Corpus**:
- [ ] Kangxi 214 radicals fully defined
- [ ] Top 3,000 characters by frequency
- [ ] Sample extension characters (CJK Ext A/B)
- [ ] Cross-orthography variant examples

**IP Considerations**:
- Contributor License Agreement for all contributors
- Clear open-source licensing (CC-BY or similar)
- No patent encumbrances

### 4.3 Timeline Considerations

| Milestone | Target | Dependencies |
|-----------|--------|--------------|
| Level 2 renderer complete | Q3 2026 | Reference implementation |
| Kangxi radical corpus | Q4 2026 | Stroke definitions |
| First UTC document submission | Q1 2027 | All above |
| IRG presentation | Mid-2027 | UTC feedback incorporated |
| DUTR status | Q3-Q4 2027 | Public review cycle |
| UTS status | 2028-2029 | Maturity demonstration |

This timeline assumes active development. Delays in reference
implementation will push all downstream dates.

### 4.4 Potential Allies

**Font Vendors**:
- Adobe (Source Han Sans/Serif, maintains CJK Type Blog)
- Google (Noto CJK, significant Unicode investment)
- Arphic Technology (pan-CJK font pioneer)
- Monotype (enterprise font solutions)

*Value proposition*: CSDL could enable component-aware font compilation,
maintaining structural metadata through the build process.

**Input Method Developers**:
- Google (Gboard, Google Japanese Input)
- Apple (iOS/macOS input methods)
- Sogou, Baidu (Chinese input)

*Value proposition*: Structural decomposition improves prediction and
suggestion algorithms for rare characters.

**Educational Technology**:
- Skritter, Pleco (Chinese learning apps)
- Kanji study applications
- Academic institutions (Chinese/Japanese linguistics)

*Value proposition*: Step-by-step character construction with coordinates
is pedagogically superior to static images.

**Academic/Research**:
- CHISE Project (Kyoto University) - extensive IDS work
- SAT Daizoko Text Database (Buddhist text digitization)
- Chinese text digitization projects

*Value proposition*: CSDL provides richer metadata than IDS alone.

**Prior Art Relationships**:
- Wenlin CDL: Wenlin Institute developed Character Description Language
  (CDL), submitted to UTC in 2003 (L2/03-404). CDL uses XML and focuses
  on font rendering. CSDL takes a different approach (line-oriented DSL,
  topological-first) but shares goals. Engagement with Wenlin could
  identify alignment opportunities or differentiation.

---

## 5. Risks and Mitigations

### 5.1 Scope Creep Concerns

**Risk**: UTC may perceive CSDL as expanding Unicode's scope into font
rendering territory, which Unicode explicitly avoids.

**Mitigation**:
- Emphasize CSDL as structural geometry, not rendering instructions
- CSDL output is positioned strokes, not filled outlines or pixels
- Explicitly state that rendering (anti-aliasing, hinting, rasterization)
  is out of scope
- Align with existing scope: Unicode already has IDS (structure) and
  CJK Strokes (stroke glyphs); CSDL bridges them

**Talking points**:
- "CSDL is IDS with coordinates, not a font format"
- "CSDL tells you where, IDS tells you what, fonts tell you how"

### 5.2 Competition with Existing Approaches

**Risk**: Wenlin CDL exists, CHISE has extensive IDS databases, various
academic projects have structural data. CSDL may be seen as reinventing
the wheel.

**Mitigation**:
- Acknowledge prior art explicitly and respectfully
- Differentiate: Wenlin CDL is XML-based font technology; CSDL is a
  line-oriented DSL for human authoring and tool interchange
- Offer import/export: CSDL can consume IDS and emit IDS
- Position as unifying layer, not replacement

**Wenlin CDL comparison**:

| Aspect | Wenlin CDL | CSDL |
|--------|------------|------|
| Format | XML | Line-oriented text |
| Primary use | Font rendering | Character description |
| Stroke model | Bezier curves | Named stroke primitives |
| IDS relation | Independent | Superset via CSDL-U |
| Turing-complete | No | No |

Both approaches have merit. CSDL's line-oriented format optimizes for
human authoring and version control (diff-friendly), while CDL's XML
optimizes for programmatic manipulation.

### 5.3 Implementation Burden

**Risk**: CJK font/tool vendors may view CSDL support as additional
burden without clear ROI.

**Mitigation**:
- Provide high-quality reference implementation (open source)
- Start with Level 1 (parser only) - minimal implementation burden
- Demonstrate concrete use cases with working prototypes
- Engage vendors early for feedback before standardization

**Burden hierarchy**:
1. Level 1 (Parser): Validate syntax, check references - easy
2. Level 2 (Renderer): Compute geometry - medium
3. Level 3 (Full): Expand to outlines - hard, but optional

Most use cases (character databases, educational tools, structural
search) only need Level 1 or Level 2.

### 5.4 Versioning and Stability

**Risk**: If CSDL evolves significantly post-standardization, fragmentation
could occur (multiple incompatible versions in the wild).

**Mitigation**:
- CSDL spec includes explicit stability guarantees:
  - Minor versions: Only metadata and orthography tags
  - Major versions: Required for new strokes/operators
- Closed registries prevent dialect proliferation
- Non-Turing guarantee is permanent (spec forbids relaxing this)

### 5.5 Adoption Chicken-and-Egg

**Risk**: Tools won't support CSDL without content; content creators
won't use CSDL without tools.

**Mitigation**:
- Bootstrap with Kangxi 214 radicals (core reusable components)
- Provide conversion tools for existing IDS databases (CHISE, cjkvi-ids)
- Target niche early adopters (educational tools, researchers) before
  mass-market tools
- Reference implementation doubles as usable tool

---

## 6. Next Steps

### Immediate (Q3 2026)

1. Complete Level 2 reference renderer
2. Define all 214 Kangxi radicals in CSDL
3. Draft UTC submission document (L2 format)

### Near-term (Q4 2026 - Q1 2027)

4. Build test corpus (top 3,000 characters)
5. Create web-based interactive demo
6. Submit document to UTC
7. Reach out to Wenlin Institute for coordination

### Medium-term (2027)

8. Respond to UTC feedback, iterate specification
9. Present to IRG
10. Pursue DUTR status after public review

### Long-term (2028+)

11. Achieve UTS status
12. Build ecosystem (tools, content, community)
13. Evaluate UAX elevation based on adoption

---

## References

### Unicode Specifications

- [Unicode Technical Committee](https://www.unicode.org/consortium/utc.html)
- [FAQ - Technical Reports Development Process](https://www.unicode.org/faq/reports_process.html)
- [UAX #38: Unicode Han Database (Unihan)](https://www.unicode.org/reports/tr38/)
- [UAX #45: U-source Ideographs](https://www.unicode.org/reports/tr45/)
- [Ideographic Research Group](https://www.unicode.org/irg/)
- [CJK Strokes Block](https://www.unicode.org/charts/nameslist/n_31C0.html)

### Related Work

- [Wenlin CDL Specification (L2/03-404)](https://www.unicode.org/L2/L2003/03404-cdl-spec.pdf)
- [CHISE Project](https://www.chise.org/)
- [cjkvi-ids (GitHub)](https://github.com/cjkvi/cjkvi-ids)
- [Chinese character description languages (Wikipedia)](https://en.wikipedia.org/wiki/Chinese_character_description_languages)

### Governance

- [RFC 3718: Unicode Consortium Procedures](https://www.rfc-editor.org/rfc/rfc3718.html)
- [Ideographic Research Group (Wikipedia)](https://en.wikipedia.org/wiki/Ideographic_Research_Group)
- [Unicode Consortium (Wikipedia)](https://en.wikipedia.org/wiki/Unicode_Consortium)

---

## Appendix: CSDL-U Profile Summary

CSDL-U is the Unicode-native syntax profile that uses IDS operators
directly. Key characteristics:

1. **IDS operators as layout operators**: No ASCII operator names
2. **No parentheses or commas**: IDS operators have fixed arity
3. **Annotation syntax for extensions**: `:4/8` for splits, `@sc(8,8)` for transforms
4. **Unicode characters only**: No pinyin aliases

Example - 明 in three representations:

```
# CSDL-ASCII (full 7-bit)
ming2 = LR(ri4, yue4)

# CSDL-ASCII (mixed)
明 ming2 = LR(日, 月)

# CSDL-U (full Unicode)
明 = ⿰日月
```

All three are semantically equivalent and mechanically interconvertible.

For standardization purposes, CSDL-U is the recommended submission format
because it builds directly on existing Unicode characters (U+2FF0-U+2FFB)
and requires no new character encoding.

---

*Document prepared for CSDL project strategic planning.*
