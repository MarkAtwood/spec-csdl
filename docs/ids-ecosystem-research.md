# IDS and Unihan Ecosystem Research

Research conducted 2026-06-21 to inform CSDL-U (Unicode-native profile) strategy.

## Executive Summary

The IDS (Ideographic Description Sequence) ecosystem is mature but has fundamental limitations that CSDL addresses. The Unihan kIDS property is actively being developed with IRG buy-in. Multiple paths to Unicode standardization exist, from lightweight Unicode Technical Notes to full Unicode Standard Annexes. CSDL's stroke-level geometry fills a gap that IDS cannot address.

---

## 1. Current IDS Usage in Unihan

### 1.1 What is the kIDS Property?

The kIDS property is a **provisional Unihan database property** designed to specify at least one Ideographic Description Sequence for every CJK ideograph in Unicode. Per [L2/21-118](https://www.unicode.org/L2/L2021/21118-kids-preliminary.pdf), this property is under active development.

**Format**: IDS sequences use 12 Ideographic Description Characters (IDCs):
- Binary operators: `⿰` (LR), `⿱` (TB), `⿲` (LMR), `⿳` (TMB), `⿴` (surround), `⿵` (surround-open-bottom), `⿶` (surround-open-top), `⿷` (surround-open-right), `⿸` (surround-upper-left), `⿹` (surround-upper-right), `⿺` (surround-lower-left)
- Overlay operator: `⿻` (overlay/superimpose)

Example: `明` = `⿰日月` (left-right composition of sun and moon)

**Grammar** (per Unicode Standard Chapter 18):
```
IDS := Ideographic | Radical | CJK_Stroke | Private_Use | U+FF1F |
       IDS_UnaryOperator IDS |
       IDS_BinaryOperator IDS IDS |
       IDS_TrinaryOperator IDS IDS IDS
```

### 1.2 Coverage Statistics

| Source | Characters | Coverage |
|--------|------------|----------|
| [BabelStone IDS](https://www.babelstone.co.uk/CJK/IDS.TXT) | 97,680 | All CJK Unified Ideographs (Unicode 16.0) |
| [CHISE-IDS](https://github.com/chise/ids) | ~90,000+ | CJK Basic + Extensions A-E |
| [cjkvi-ids](https://github.com/cjkvi/cjkvi-ids) | ~90,000+ | CJK Basic + Extensions A-F |
| [hfhchan/ids](https://github.com/hfhchan/ids) | varies | GlyphWiki-derived data |

**Note**: The official kIDS property in Unihan was targeted for Unicode 17.0 (2024), but as of 2025/2026, appears to still be provisional. The primary blocking factor is IRG buy-in and the need to encode additional IDCs and IDS component characters.

### 1.3 Limitations of Current IDS

**Fundamental limitations** (per [Unicode Chapter 18](https://www.unicode.org/versions/Unicode16.0.0/core-spec/chapter-18/) and [community analysis](https://ansuz.sooke.bc.ca/entry/228)):

1. **No geometry/positioning information**: IDS specifies *which* components and *general layout*, but not precise positioning, proportions, or stroke adjustments

2. **No stroke-level detail**: Cannot distinguish stroke variants, shapes, or order

3. **Component customization lost**: Even when a character appears to contain a standard component (e.g., `月` in `能`), the component often requires visual modification that IDS cannot express

4. **Ambiguous overlay operator**: `⿻` indicates two components overlay but doesn't specify relative positioning

5. **Multiple decompositions possible**: Many characters can be described in more than one way; no canonical form

6. **Not renderable**: "The IDS describes the ideograph in the abstract form. It is not interpreted as a composed character and does not imply any specific form of rendering." (Unicode Standard)

**What IDS IS good for**:
- Character identification and lookup
- Dictionary indexing by component
- IRG unification work (first-approximation matching)
- Pedagogical analysis

---

## 2. IRG Working Documents and Proposals

### 2.1 Ideographic Research Group (IRG)

The [IRG](https://www.unicode.org/irg/) is a subgroup of ISO/IEC JTC 1/SC 2/WG 2, responsible for:
- Developing and reviewing Han ideograph repertoires
- CJK unification decisions
- Extension block development (Extensions A through J and beyond)

**Key personnel** (as of 2025):
- **Convenor**: Dr Ken Lunde (lunde@unicode.org) - since 2024
- **Chief Editor**: CHEN Zhuang (chenzh-zhuang@163.com)
- **IWDS Editor**: Yi BAI (yibai.thu@gmail.com)

**Active member bodies**: PRC, ROK, Hong Kong SAR, Macao SAR, TCA (Taiwan), Vietnam, SAT (Japan), UK, US, Unicode Consortium

### 2.2 IDS Extension Proposals

**[L2/12-081](http://www.unicode.org/L2/L2012/12081-ids.html)** (Eric Muller, Adobe, 2012):
- Extended IDS to siniform scripts (Tangut, Jurchen, Khitan)
- No new operators, but broadened scope beyond Han

**[L2/21-118](https://www.unicode.org/L2/L2021/21118-kids-preliminary.pdf)** (preliminary kIDS proposal):
- Proposed encoding new IDCs
- Proposed new CJK Unified Ideographs as IDS components
- Target: kIDS property for every ideograph

**Unicode 15.1 (2023)**: Five new IDCs added (U+2FFC-U+2FFF):
- `⿼` = overlapping left-to-right
- `⿽` = overlapping right-to-left
- `⿾` = overlapping top-to-bottom
- `⿿` = overlapping bottom-to-top

**Current work** (per [IRG N2878R](https://www.unicode.org/irg/)):
- CJK Unified Ideographs Components-A and Components-B blocks proposed
- Encoding components that currently exist only as Private Use Area characters

### 2.3 IDS + Geometry/Strokes Discussions

**Finding**: No formal IRG/UTC proposal exists to add geometry or stroke information to IDS. The Unicode position is clear: IDS is structural/abstract, not rendering-focused.

The IRG [Principles and Procedures (PnP) v17](https://unicode.org/irg/docs/n2652-PPv17.pdf) establishes:
- Three-dimensional unification model: semantic (X), abstract shape (Y), actual shape (Z)
- IDS used for "first-approximation machine-generated unification"
- No provisions for stroke-level or geometric data

---

## 3. Existing IDS Parsers and Tools

### 3.1 Data Sources

| Repository | Language | License | Notes |
|------------|----------|---------|-------|
| [BabelStone IDS](https://www.babelstone.co.uk/CJK/IDS.TXT) | Data (TXT) | Public Domain | 97,680 chars, Unicode 16.0, maintained by Andrew West (1960-2025) |
| [cjkvi-ids](https://github.com/cjkvi/cjkvi-ids) | Data (TXT) | GPLv2 (CHISE-derived) | Multiple variants, CDP PUA support |
| [CHISE-IDS](https://github.com/chise/ids) | Data (TXT) | GPLv2 | Original authoritative source |
| [hfhchan/ids](https://github.com/hfhchan/ids) | Data (TXT) | Unspecified | GlyphWiki-derived, IRG PNP compliant |

### 3.2 Parser/Tool Libraries

| Project | Language | Purpose |
|---------|----------|---------|
| [parse-ids](https://github.com/tomcumming/parse-ids) | TypeScript | Parser for CHISE-format IDS files |
| [ids-tools](https://github.com/jimmymasaru/ids-tools) | Node.js | Query IDS for ideographs |
| [kawabata/ids](https://github.com/kawabata/ids) | Emacs Lisp | IDS checker, normalizer, equivalence testing |
| [ids-edit](https://github.com/kawabata/ids-edit) | Emacs Lisp | IDS composition/decomposition editing |
| [Radically](https://github.com/Radically/radically) | JS | Component-based CJK character search engine |

### 3.3 Extended IDS and Beyond

**None of the above handle geometry or strokes**. For those, different systems exist:

| System | Description | Coverage |
|--------|-------------|----------|
| [Wenlin CDL](https://wenlin.com/cdl/) | XML-based stroke description with coordinates | 86,416+ characters |
| [GlyphWiki KAGE](https://glyphwiki.org/) | Stroke vector format for font generation | 100,000+ glyphs |
| [makemeahanzi](https://github.com/skishore/makemeahanzi) | SVG stroke paths + IDS decomposition | 9,000+ common chars |
| [zi.tools](https://zi.tools/) | Interactive reference with component analysis | Comprehensive lookup |

**CDL (Character Description Language)** is closest to CSDL conceptually:
- XML-based
- ~50 stroke types with 2D coordinates (0-128 grid)
- Stroke order defined
- Component nesting supported
- Output: SVG, EPS, scalable fonts

---

## 4. Unicode Standardization Paths

### 4.1 Document Types

| Type | Status | Normative? | Governance |
|------|--------|------------|------------|
| **UAX** (Unicode Standard Annex) | Part of Unicode Standard | Yes | UTC approval, versioned with Unicode |
| **UTS** (Unicode Technical Standard) | Independent specification | Yes (for UTS itself) | UTC approval, independent versioning |
| **UTR** (Unicode Technical Report) | Informative | No | UTC approval |
| **UTN** (Unicode Technical Note) | Informative | No | **Author responsibility**, no TC review |

### 4.2 Process for Each Type

**Unicode Technical Note (UTN)** - Easiest path:
- Author-maintained, no formal review
- "Publication does not imply endorsement by the Unicode Consortium"
- Submit via [unicode.org/notes](https://www.unicode.org/notes/)
- Template provided but not required
- Can be any format (HTML, PDF)
- Good for: documentation, proposals, early-stage work

**Unicode Technical Report (UTR/UTS/UAX)** - Full process:
1. Working document stage (UTC internal)
2. Proposed Draft (PDUTR) - earliest public review
3. Draft (DUTR) - approved for public review
4. Approved - published
5. May advance to UTS or UAX

**Approval requirements**:
- Majority vote in UTC
- Supermajority to overturn previous decisions
- Most decisions by consensus

**Timeline**: Not specified, but typically 1-3+ years for full standardization

### 4.3 Precedents

**CLDR (Common Locale Data Repository)**:
- Started as external project (IBM)
- Became UTS #35 (Unicode Locale Data Markup Language)
- Now maintained by CLDR Technical Committee under Unicode

**ICU (International Components for Unicode)**:
- Started at IBM (1999)
- Joined Unicode Consortium 2016 as ICU-TC
- Implements multiple UTSes (UCA, normalization, etc.)

**Emoji**:
- External pressure (Japan carriers, Apple)
- Created Emoji Subcommittee
- Now UTR #51 (Unicode Emoji)
- Open public submission process

### 4.4 What CSDL Would Need

**For UTN (lowest barrier)**:
- Polished specification document
- Working reference implementation
- Submit to unicode.org/notes

**For UTS/UAX (full standard)**:
- UTC membership or liaison relationship
- Champion within UTC (ideally CJK Working Group)
- Implementation experience
- Multiple implementors preferred
- IRG consultation (given CJK scope)
- Multi-year commitment

**Key contacts to engage**:
1. **Ken Lunde** - IRG Convenor, UTC CJK & Unihan Working Group Chair
2. **IRG member bodies** - especially PRC, Japan (SAT), Taiwan (TCA)
3. **UTC CJK & Unihan Working Group** members

---

## 5. Strategic Recommendations for CSDL

### 5.1 Positioning

**CSDL fills a gap IDS cannot**:
- IDS = structural abstraction (component + layout)
- CSDL = precise specification (stroke geometry + layout + components)

**Not competing, complementary**:
- IDS is for identification/lookup/unification
- CSDL is for rendering/fonts/stroke-order education

**Analogy**: IDS is like HTML (structure), CSDL is like CSS+SVG (presentation)

### 5.2 Recommended Path

**Phase 1: Establish credibility (now)**
1. Publish CSDL as **Unicode Technical Note**
   - Low barrier, immediate visibility
   - Demonstrates Unicode-awareness
   - Creates citable reference

2. Create IDS-compatible mode (CSDL-U)
   - Use IDC operators where possible
   - Extend with CSDL-specific operators using PUA or registered prefixes
   - Show clear mapping: CSDL -> IDS (lossy) and IDS -> CSDL (enriched)

3. Build reference corpus
   - At minimum: Kangxi radicals + common characters
   - Show side-by-side with IDS

**Phase 2: Community building (6-12 months)**
1. Engage font/rendering community
   - GlyphWiki maintainers
   - Open-source CJK font projects
   - Educational technology (stroke order apps)

2. Present at Unicode events
   - Unicode Technology Workshop (UTW)
   - IUC (Internationalization & Unicode Conference)

3. Publish tools
   - CSDL -> SVG renderer
   - IDS -> CSDL converter (inferring default geometry)
   - CSDL validator

**Phase 3: Standardization (1-3 years)**
1. Contact Ken Lunde and CJK Working Group
2. Submit as formal UTC document (L2/xx-xxx)
3. Request liaison status if not full membership
4. Target: UTS (independent standard) rather than UAX (part of Unicode Standard)

### 5.3 Key Differentiators to Emphasize

1. **Closed stroke registry** (38 strokes) vs open-ended IDS components
2. **Explicit geometry** (12x12 grid, transforms) vs implicit layout
3. **Stroke order** vs unordered components
4. **Renderable by design** vs abstract-only
5. **Multiple orthography support** (`@Hani`, `@Jpan`, etc.)

### 5.4 Potential Challenges

1. **"Not invented here"** - IRG has their own processes
2. **Scope creep concerns** - Unicode prefers minimal normative additions
3. **Implementation burden** - new format = new parsers/renderers
4. **Existing CDL** - Wenlin CDL exists, why another?

**Mitigation**:
- Position as complementary to IDS, not replacement
- Emphasize open license and reference implementation
- Show clear use cases IDS cannot solve
- Acknowledge CDL heritage, show improvements (open spec, stroke registry, Unicode alignment)

---

## 6. Key Contacts and Stakeholders

### Unicode/IRG

| Name | Role | Contact |
|------|------|---------|
| Ken Lunde | IRG Convenor, UTC CJK WG Chair | lunde@unicode.org |
| CHEN Zhuang | IRG Chief Editor | chenzh-zhuang@163.com |
| Yi BAI | IWDS Editor | yibai.thu@gmail.com |

### Tool/Data Maintainers

| Project | Maintainer | Notes |
|---------|------------|-------|
| CHISE | Kyoto University | Original IDS database |
| cjkvi-ids | kawabata | Active GitHub maintenance |
| GlyphWiki | Community | KAGE format, glyph hosting |
| makemeahanzi | skishore | Stroke animations |

### Organizations

| Organization | Relevance |
|--------------|-----------|
| Unicode Consortium | Standardization body |
| IRG member bodies | CJK stakeholders |
| Wenlin Institute | CDL creators, potential collaborators |
| SAT (Japan) | Buddhist text digitization, heavy CJK users |

---

## 7. References

### Unicode Documents
- [UAX #38: Unicode Han Database (Unihan)](https://www.unicode.org/reports/tr38/)
- [Unicode Chapter 18: East Asian Scripts](https://www.unicode.org/versions/Unicode16.0.0/core-spec/chapter-18/)
- [L2/21-118: Preliminary kIDS Proposal](https://www.unicode.org/L2/L2021/21118-kids-preliminary.pdf)
- [L2/12-081: Extensions to IDS](http://www.unicode.org/L2/L2012/12081-ids.html)
- [IRG Principles and Procedures v17](https://unicode.org/irg/docs/n2652-PPv17.pdf)
- [Unicode Technical Notes](https://www.unicode.org/notes/)
- [FAQ: Technical Reports Process](https://www.unicode.org/faq/reports_process.html)

### IDS Data Sources
- [BabelStone IDS Database](https://www.babelstone.co.uk/CJK/IDS.TXT)
- [cjkvi-ids (GitHub)](https://github.com/cjkvi/cjkvi-ids)
- [CHISE-IDS (GitHub)](https://github.com/chise/ids)

### Tools and Libraries
- [kawabata/ids](https://github.com/kawabata/ids)
- [parse-ids](https://github.com/tomcumming/parse-ids)
- [makemeahanzi](https://github.com/skishore/makemeahanzi)
- [GlyphWiki](https://glyphwiki.org/)
- [zi.tools](https://zi.tools/)

### Related Character Description Systems
- [Wenlin CDL Specification](https://www.unicode.org/L2/L2003/03404-cdl-spec.pdf)
- [KAGE Engine](https://github.com/HowardZorn/kage-engine)

### Analysis
- [IDS Limitations Discussion](https://ansuz.sooke.bc.ca/entry/228)
- [Ken Lunde: 2024 State of the Unification](https://ken-lunde.medium.com/2024-state-of-the-unification-report-e1b8427d3267)
- [Wikipedia: Ideographic Description Characters](https://en.wikipedia.org/wiki/Ideographic_Description_Characters_(Unicode_block))
