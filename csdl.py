#!/usr/bin/env python3
"""
CSDL Reference Parser — Level 1 Conformance
Validates syntax and semantic constraints. Accept/reject only, no rendering.

Usage: python csdl.py <file.csdl>
Exit 0 = valid, Exit 1 = invalid (errors printed to stderr)
"""

import re
import sys
from dataclasses import dataclass, field
from typing import Optional

# =============================================================================
# Stroke Registry (38 strokes: 12 base + 26 compound)
# =============================================================================

STROKE_REGISTRY = {
    # 12 base strokes (2 points each, except quan which needs 3)
    "heng": 2, "shu": 2, "pie": 2, "na": 2, "dian": 2, "ti": 2,
    "gou": 2, "wan": 2, "zhe": 2, "xie": 2, "wo": 2, "quan": 3,
    # 26 compound strokes (points = segments + 1)
    # Single-fold (12): 3 points
    "heng-zhe": 3, "heng-pie": 3, "heng-gou": 3, "shu-zhe": 3,
    "shu-wan": 3, "shu-ti": 3, "shu-gou": 3, "pie-zhe": 3,
    "pie-dian": 3, "wan-gou": 3, "xie-gou": 3, "wo-gou": 3,
    # Double-fold (8): 4 points
    "heng-zhe-zhe": 4, "heng-zhe-wan": 4, "heng-zhe-ti": 4,
    "heng-zhe-gou": 4, "heng-xie-gou": 4, "shu-zhe-zhe": 4,
    "shu-zhe-pie": 4, "shu-wan-gou": 4,
    # Triple-fold (5): 5 points
    "heng-zhe-zhe-zhe": 5, "heng-zhe-zhe-pie": 5, "heng-zhe-wan-gou": 5,
    "heng-pie-wan-gou": 5, "shu-zhe-zhe-gou": 5,
    # Quadruple-fold (1): 6 points
    "heng-zhe-zhe-zhe-gou": 6,
    # Kana extensions
    "wan-quan": 4,
}

# =============================================================================
# Lexer
# =============================================================================

TOKEN_PATTERNS = [
    ("COMMENT", r"#[^\n]*"),
    ("NL", r"\n"),
    ("WS", r"[ \t]+"),
    ("CODEPOINT", r"U\+[0-9A-Fa-f]{4,6}"),
    ("KEYWORD", r"@csdl|@ortho|@alias|@comp|@char|@end|build:|close:|rad:|sc:|freq:|ortho:|x-[a-z]+:"),
    ("FROM_EXPR", r"from_expr"),
    ("LAYOUT_OP", r"LR3|TB3|LR|TB|SUR|OVR|GRP|GRID"),
    ("XFORM_OP", r"sc(?=\()|sh(?=\()|sk(?=\()"),
    ("STROKE_OP", r"S"),
    ("SUR_SIDE", r"full|tl|tr|top|right|left|bot|bl|br"),
    ("GRID_SPEC", r"/24|/12"),
    ("PARAM", r"sx=|sy=|dx=|dy=|kx=|ky="),
    ("COORD", r"\[[0-9]+,[0-9]+\]"),
    ("SPLIT", r"[0-9]+/[0-9]+(?:/[0-9]+)?"),
    ("INT", r"-?[0-9]+"),
    ("CJK", r"[\u3400-\u9fff\uf900-\ufaff]|[\U00020000-\U0002fa1f]|[\U00030000-\U0003134f]|[\U00031350-\U000323af]"),
    ("PINYIN", r"[a-z]+[1-5](?:[a-z]+[1-5])*"),
    ("VARIANT_TAG", r"\.[a-z][a-z0-9]*"),
    ("STROKE_NAME", r"x-[a-z]+(?:-[a-z]+)*|[a-z]+(?:-[a-z]+)*"),
    ("ORTHO_TAG", r"x-[A-Za-z]+|[A-Z][a-z]{3}"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA", r","),
    ("EQUALS", r"="),
    ("DOT", r"\."),
]

TOKEN_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_PATTERNS))


@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int


def tokenize(text: str) -> list[Token]:
    tokens = []
    line, col = 1, 1
    for match in TOKEN_RE.finditer(text):
        kind = match.lastgroup
        value = match.group()
        if kind == "NL":
            tokens.append(Token(kind, value, line, col))
            line += 1
            col = 1
        elif kind == "WS":
            col += len(value)
        elif kind == "COMMENT":
            col += len(value)
        else:
            tokens.append(Token(kind, value, line, col))
            col += len(value)
    return tokens


# =============================================================================
# Parser
# =============================================================================

@dataclass
class ParseError(Exception):
    message: str
    line: int
    col: int

    def __str__(self):
        return f"line {self.line}:{self.col}: {self.message}"


@dataclass
class Node:
    kind: str
    value: str = ""
    children: list["Node"] = field(default_factory=list)
    line: int = 0
    col: int = 0
    meta: dict = field(default_factory=dict)


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = [t for t in tokens if t.type != "NL" or True]  # keep NL for line tracking
        self.pos = 0
        self.definitions: dict[str, Node] = {}
        self.aliases: dict[str, str] = {}
        self.components: set[str] = set()
        self.errors: list[ParseError] = []
        self.grid_mode = 12  # current grid (12 or 24)
        self.file_ortho: Optional[str] = None
        self.char_defs: list[tuple[str, Optional[str]]] = []  # (codepoint, ortho)

    def current(self) -> Optional[Token]:
        while self.pos < len(self.tokens) and self.tokens[self.pos].type in ("WS", "COMMENT"):
            self.pos += 1
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek(self, offset: int = 0) -> Optional[Token]:
        p = self.pos + offset
        while p < len(self.tokens) and self.tokens[p].type in ("WS", "COMMENT"):
            p += 1
        return self.tokens[p] if p < len(self.tokens) else None

    def consume(self, expected_type: Optional[str] = None) -> Token:
        tok = self.current()
        if tok is None:
            raise ParseError("unexpected end of input", 0, 0)
        if expected_type and tok.type != expected_type:
            raise ParseError(f"expected {expected_type}, got {tok.type}", tok.line, tok.col)
        self.pos += 1
        return tok

    def skip_blank_lines(self):
        while self.current() and self.current().type == "NL":
            self.pos += 1

    def error(self, msg: str, tok: Optional[Token] = None):
        t = tok or self.current()
        line, col = (t.line, t.col) if t else (0, 0)
        self.errors.append(ParseError(msg, line, col))

    def parse(self) -> Node:
        root = Node("file")
        self.skip_blank_lines()

        # Optional @csdl declaration
        if self.current() and self.current().type == "KEYWORD" and self.current().value == "@csdl":
            root.children.append(self.parse_csdl_decl())
            self.skip_blank_lines()

        # Optional @ortho declaration
        if self.current() and self.current().type == "KEYWORD" and self.current().value == "@ortho":
            root.children.append(self.parse_ortho_decl())
            self.skip_blank_lines()

        # Definitions
        while self.current():
            self.skip_blank_lines()
            if not self.current():
                break
            tok = self.current()
            if tok.type == "KEYWORD":
                if tok.value == "@alias":
                    root.children.append(self.parse_alias())
                elif tok.value == "@comp":
                    root.children.append(self.parse_comp_block())
                elif tok.value == "@char":
                    root.children.append(self.parse_char_block())
                else:
                    self.error(f"unexpected keyword: {tok.value}")
                    self.pos += 1
            elif tok.type in ("CODEPOINT", "CJK"):
                root.children.append(self.parse_char_inline())
            else:
                self.error(f"unexpected token: {tok.value}")
                self.pos += 1
            self.skip_blank_lines()

        return root

    def parse_csdl_decl(self) -> Node:
        tok = self.consume("KEYWORD")  # @csdl
        ver = self.consume("INT") if self.current() and self.current().type == "INT" else None
        # skip version parsing details
        while self.current() and self.current().type not in ("NL",):
            self.pos += 1
        return Node("csdl_decl", ver.value if ver else "1.0", line=tok.line, col=tok.col)

    def parse_ortho_decl(self) -> Node:
        tok = self.consume("KEYWORD")  # @ortho
        if self.file_ortho is not None:
            self.error("duplicate @ortho declaration", tok)
        ortho = self.consume("ORTHO_TAG")
        self.file_ortho = ortho.value
        return Node("ortho_decl", ortho.value, line=tok.line, col=tok.col)

    def parse_alias(self) -> Node:
        tok = self.consume("KEYWORD")  # @alias
        name = self.parse_comp_name()
        self.consume("EQUALS")
        target = self.consume("CJK")
        if name in self.aliases:
            self.error(f"duplicate alias: {name}", tok)
        if name in self.components:
            self.error(f"alias name conflicts with component: {name}", tok)
        self.aliases[name] = target.value
        return Node("alias", name, line=tok.line, col=tok.col, meta={"target": target.value})

    def parse_comp_name(self) -> str:
        parts = []
        tok = self.current()
        if tok.type == "CJK":
            parts.append(self.consume().value)
        elif tok.type == "PINYIN":
            parts.append(self.consume().value)
        elif tok.type == "STROKE_NAME":  # might be pinyin without tone
            parts.append(self.consume().value)
        else:
            self.error(f"expected component name, got {tok.type}")
            return ""
        # Variant tags
        while self.current() and self.current().type == "VARIANT_TAG":
            parts.append(self.consume().value)
        return "".join(parts)

    def parse_comp_block(self) -> Node:
        tok = self.consume("KEYWORD")  # @comp
        name = self.parse_comp_name()
        if name in self.components:
            self.error(f"duplicate component: {name}", tok)
        if name in self.aliases:
            self.error(f"component name conflicts with alias: {name}", tok)
        self.components.add(name)

        # Grid spec?
        grid = 12
        if self.current() and self.current().type == "GRID_SPEC":
            grid = 24 if self.consume().value == "/24" else 12

        self.skip_blank_lines()
        node = Node("comp", name, line=tok.line, col=tok.col, meta={"grid": grid})
        self.grid_mode = grid

        # Parse body
        build_line = None
        close_stroke = None
        strokes = {}
        expr = None
        is_expr_form = False

        while self.current():
            self.skip_blank_lines()
            if not self.current():
                break
            t = self.current()
            if t.type == "KEYWORD" and t.value == "@end":
                break

            if t.type == "KEYWORD" and t.value == "build:":
                self.consume()
                if self.current() and self.current().type == "FROM_EXPR":
                    self.consume()
                    is_expr_form = True
                    if grid == 24:
                        self.error("/24 and build: from_expr are mutually exclusive", t)
                else:
                    build_line = []
                    while self.current() and self.current().type in ("STROKE_NAME", "PINYIN"):
                        build_line.append(self.consume().value)
            elif t.type == "KEYWORD" and t.value == "close:":
                self.consume()
                if self.current() and self.current().type in ("STROKE_NAME", "PINYIN"):
                    close_stroke = self.consume().value
            elif t.type == "KEYWORD" and t.value.startswith(("rad:", "sc:", "freq:", "ortho:", "x-")):
                key = self.consume().value.rstrip(":")
                node.meta[key] = self.parse_meta_value()
            elif t.type in ("STROKE_NAME", "PINYIN") and self.peek(1) and self.peek(1).type == "EQUALS":
                # Stroke def: s1 = S(...)
                sid = self.consume().value
                self.consume("EQUALS")
                stroke = self.parse_stroke_expr()
                strokes[sid] = stroke
                node.children.append(Node("stroke_def", sid, [stroke], line=t.line, col=t.col))
            elif t.type == "LAYOUT_OP" or (t.type in ("CJK", "PINYIN", "STROKE_NAME") and is_expr_form):
                expr = self.parse_expr()
                node.children.append(expr)
            elif t.type == "NL":
                self.pos += 1
            else:
                self.pos += 1  # skip unknown

        if self.current() and self.current().type == "KEYWORD" and self.current().value == "@end":
            self.consume()

        # Validate build line
        if is_expr_form:
            if strokes:
                self.error("expression-form block cannot have stroke definitions", tok)
            if close_stroke:
                self.error("close: cannot appear in expression-form block", tok)
        else:
            if build_line is not None:
                defined = set(strokes.keys())
                build_set = set(build_line)
                if defined != build_set:
                    self.error(f"build: line strokes {build_set} != defined strokes {defined}", tok)
            if close_stroke and close_stroke not in strokes:
                self.error(f"close: references undefined stroke {close_stroke}", tok)

        self.grid_mode = 12
        return node

    def parse_char_block(self) -> Node:
        tok = self.consume("KEYWORD")  # @char
        codepoint = self.consume("CODEPOINT") if self.current().type == "CODEPOINT" else self.consume("CJK")
        pinyin = self.parse_comp_name()

        self.skip_blank_lines()
        node = Node("char_block", codepoint.value, line=tok.line, col=tok.col, meta={"pinyin": pinyin})

        # Similar to comp block
        build_line = None
        strokes = {}
        is_expr_form = False

        while self.current():
            self.skip_blank_lines()
            if not self.current():
                break
            t = self.current()
            if t.type == "KEYWORD" and t.value == "@end":
                break

            if t.type == "KEYWORD" and t.value == "build:":
                self.consume()
                if self.current() and self.current().type == "FROM_EXPR":
                    self.consume()
                    is_expr_form = True
                else:
                    build_line = []
                    while self.current() and self.current().type in ("STROKE_NAME", "PINYIN"):
                        build_line.append(self.consume().value)
            elif t.type == "KEYWORD" and t.value.startswith(("rad:", "sc:", "freq:", "ortho:", "x-")):
                key = self.consume().value.rstrip(":")
                node.meta[key] = self.parse_meta_value()
            elif t.type in ("STROKE_NAME", "PINYIN") and self.peek(1) and self.peek(1).type == "EQUALS":
                sid = self.consume().value
                self.consume("EQUALS")
                stroke = self.parse_stroke_expr()
                strokes[sid] = stroke
                node.children.append(Node("stroke_def", sid, [stroke], line=t.line, col=t.col))
            elif t.type == "LAYOUT_OP":
                expr = self.parse_expr()
                node.children.append(expr)
            elif t.type == "NL":
                self.pos += 1
            else:
                self.pos += 1

        if self.current() and self.current().type == "KEYWORD" and self.current().value == "@end":
            self.consume()

        # Check duplicate char defs
        ortho = node.meta.get("ortho")
        key = (codepoint.value, ortho)
        if key in self.char_defs:
            self.error(f"duplicate definition for {codepoint.value} with ortho={ortho}", tok)
        self.char_defs.append(key)

        return node

    def parse_char_inline(self) -> Node:
        tok = self.current()
        codepoint = self.consume().value  # CODEPOINT or CJK
        pinyin = self.parse_comp_name()
        self.consume("EQUALS")
        expr = self.parse_expr()
        node = Node("char_inline", codepoint, [expr], line=tok.line, col=tok.col, meta={"pinyin": pinyin})

        # Trailing metadata
        while self.current() and self.current().type == "KEYWORD" and self.current().value.startswith(("rad:", "sc:", "freq:", "ortho:", "x-")):
            key = self.current().value.rstrip(":")
            self.consume()
            node.meta[key] = self.parse_meta_value()

        # Check duplicate char defs
        ortho = node.meta.get("ortho")
        key = (codepoint, ortho)
        if key in self.char_defs:
            self.error(f"duplicate definition for {codepoint} with ortho={ortho}", tok)
        self.char_defs.append(key)

        return node

    def parse_meta_value(self) -> str:
        parts = []
        while self.current() and self.current().type in ("INT", "ORTHO_TAG", "STROKE_NAME", "PINYIN", "COMMA", "CJK"):
            parts.append(self.consume().value)
            if not self.current() or self.current().type in ("NL", "KEYWORD"):
                break
        return "".join(parts)

    def parse_expr(self) -> Node:
        tok = self.current()
        if tok.type == "LAYOUT_OP":
            return self.parse_layout_expr()
        elif tok.type == "XFORM_OP":
            return self.parse_xform_expr()
        elif tok.type == "STROKE_OP":
            return self.parse_stroke_expr()
        elif tok.type in ("CJK", "PINYIN", "STROKE_NAME"):
            name = self.parse_comp_name()
            return Node("ref", name, line=tok.line, col=tok.col)
        else:
            self.error(f"expected expression, got {tok.type}")
            self.pos += 1
            return Node("error")

    def parse_layout_expr(self) -> Node:
        tok = self.consume("LAYOUT_OP")
        op = tok.value
        self.consume("LPAREN")
        children = [self.parse_expr()]
        while self.current() and self.current().type == "COMMA":
            self.consume()
            # Check for split or side
            if self.current() and self.current().type == "SPLIT":
                break
            if self.current() and self.current().type == "SUR_SIDE":
                break
            if self.current() and self.current().type == "INT":
                # Could be inset for SUR or part of expression
                if op == "SUR":
                    break
            children.append(self.parse_expr())

        meta = {}
        # Parse optional split
        if self.current() and self.current().type == "SPLIT":
            split = self.consume().value
            meta["split"] = split
            self.validate_split(split, op, tok)

        # Parse SUR side and inset
        if op == "SUR":
            if self.current() and self.current().type == "SUR_SIDE":
                meta["side"] = self.consume().value
            if self.current() and self.current().type == "COMMA":
                self.consume()
                if self.current() and self.current().type == "INT":
                    inset = int(self.consume().value)
                    meta["inset"] = inset
                    if not (0 <= inset <= 6):
                        self.error(f"inset must be 0-6, got {inset}", tok)

        self.consume("RPAREN")

        # Validate child count
        if op in ("LR", "TB", "OVR") and len(children) != 2:
            self.error(f"{op} requires exactly 2 children, got {len(children)}", tok)
        elif op in ("LR3", "TB3") and len(children) != 3:
            self.error(f"{op} requires exactly 3 children, got {len(children)}", tok)
        elif op == "SUR" and len(children) != 2:
            self.error(f"SUR requires exactly 2 children, got {len(children)}", tok)
        elif op == "GRP" and len(children) < 2:
            self.error(f"GRP requires at least 2 children, got {len(children)}", tok)
        elif op == "GRID" and len(children) != 4:
            self.error(f"GRID requires exactly 4 children, got {len(children)}", tok)

        return Node(op, "", children, line=tok.line, col=tok.col, meta=meta)

    def validate_split(self, split: str, op: str, tok: Token):
        parts = [int(x) for x in split.split("/")]
        if any(p <= 0 for p in parts):
            self.error(f"split values must be positive, got {split}", tok)
        if op in ("LR", "TB") and len(parts) != 2:
            self.error(f"{op} split must have 2 parts, got {len(parts)}", tok)
        elif op in ("LR3", "TB3") and len(parts) != 3:
            self.error(f"{op} split must have 3 parts, got {len(parts)}", tok)

    def parse_xform_expr(self) -> Node:
        tok = self.consume("XFORM_OP")
        op = tok.value
        self.consume("LPAREN")
        child = self.parse_expr()
        params = {}
        while self.current() and self.current().type == "COMMA":
            self.consume()
            if self.current() and self.current().type == "PARAM":
                pname = self.consume().value.rstrip("=")
                pval = int(self.consume("INT").value)
                params[pname] = pval
                if not (-12 <= pval <= 24):
                    self.error(f"transform param must be -12 to 24, got {pval}", tok)
        self.consume("RPAREN")
        return Node(op, "", [child], line=tok.line, col=tok.col, meta=params)

    def parse_stroke_expr(self) -> Node:
        tok = self.consume("STROKE_OP")
        self.consume("LPAREN")
        name_tok = self.consume("STROKE_NAME")
        name = name_tok.value

        # Validate stroke name
        if not name.startswith("x-") and name not in STROKE_REGISTRY:
            self.error(f"unknown stroke: {name}", name_tok)

        coords = []
        while self.current() and self.current().type == "COORD":
            coord = self.consume().value
            x, y = map(int, coord.strip("[]").split(","))
            max_val = self.grid_mode
            if x < 0 or x > max_val or y < 0 or y > max_val:
                self.error(f"coordinate out of range 0-{max_val}: {coord}", tok)
            coords.append((x, y))

        width = 1
        if self.current() and self.current().type == "INT":
            width = int(self.consume().value)
            if width not in (0, 1, 2):
                self.error(f"width must be 0, 1, or 2, got {width}", tok)

        self.consume("RPAREN")

        # Validate point count
        if name in STROKE_REGISTRY:
            expected = STROKE_REGISTRY[name]
            if len(coords) != expected:
                self.error(f"stroke {name} requires {expected} points, got {len(coords)}", name_tok)

        return Node("stroke", name, line=tok.line, col=tok.col, meta={"coords": coords, "width": width})


# =============================================================================
# Semantic Validator
# =============================================================================

class Validator:
    def __init__(self, root: Node, aliases: dict, components: set):
        self.root = root
        self.aliases = aliases
        self.components = components
        self.errors: list[str] = []
        self.refs: dict[str, set[str]] = {}  # component -> set of refs

    def validate(self) -> list[str]:
        self.collect_refs(self.root)
        self.check_refs()
        self.check_cycles()
        return self.errors

    def collect_refs(self, node: Node):
        if node.kind == "comp":
            self.refs[node.value] = set()
            for child in node.children:
                self.collect_refs_in_expr(node.value, child)
        for child in node.children:
            self.collect_refs(child)

    def collect_refs_in_expr(self, comp_name: str, node: Node):
        if node.kind == "ref":
            self.refs[comp_name].add(node.value)
        for child in node.children:
            self.collect_refs_in_expr(comp_name, child)

    def check_refs(self):
        all_names = self.components | set(self.aliases.keys())
        for comp, refs in self.refs.items():
            for ref in refs:
                # Resolve alias
                resolved = self.aliases.get(ref, ref)
                if resolved not in self.components and ref not in all_names:
                    # Allow CJK characters as implicit components
                    if not (len(ref) == 1 and ord(ref) > 0x3000):
                        self.errors.append(f"unresolved reference: {ref} in {comp}")

    def check_cycles(self):
        # Build dependency graph with alias resolution
        graph = {}
        for comp, refs in self.refs.items():
            resolved = set()
            for ref in refs:
                resolved.add(self.aliases.get(ref, ref))
            graph[comp] = resolved

        # DFS for cycles
        visited = set()
        path = set()

        def dfs(node):
            if node in path:
                self.errors.append(f"cycle detected involving: {node}")
                return
            if node in visited:
                return
            path.add(node)
            for dep in graph.get(node, []):
                dfs(dep)
            path.remove(node)
            visited.add(node)

        for comp in graph:
            dfs(comp)


# =============================================================================
# Main
# =============================================================================

def parse_file(path: str) -> tuple[bool, list[str]]:
    with open(path, encoding="utf-8") as f:
        text = f.read()

    tokens = tokenize(text)
    parser = Parser(tokens)
    root = parser.parse()

    errors = [str(e) for e in parser.errors]

    if not errors:
        validator = Validator(root, parser.aliases, parser.components)
        errors.extend(validator.validate())

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: csdl.py <file.csdl>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    valid, errors = parse_file(path)

    if valid:
        print(f"OK: {path}")
        sys.exit(0)
    else:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
