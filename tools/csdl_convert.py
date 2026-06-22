#!/usr/bin/env python3
"""
CSDL Profile Converter — CSDL-ASCII ↔ CSDL-U

Converts between CSDL-ASCII (LR(日, 月)) and CSDL-U (⿰日月) profiles.
Both profiles are semantically equivalent per csdl-spec.md §1.5.

Usage:
    python csdl_convert.py --to-u input.csdl > output.csdl-u
    python csdl_convert.py --to-ascii input.csdl-u > output.csdl
"""

import re
import sys
from dataclasses import dataclass
from typing import Optional

# =============================================================================
# Operator Mappings (from csdl-spec.md §1.5)
# =============================================================================

# ASCII operator -> IDS character
ASCII_TO_IDS = {
    "LR": "⿰",
    "TB": "⿱",
    "LR3": "⿲",
    "TB3": "⿳",
    "OVR": "⿻",
}

# SUR side variants -> IDS character
SUR_SIDE_TO_IDS = {
    "full": "⿴",
    "top": "⿵",
    "bot": "⿶",
    "left": "⿷",
    "tl": "⿸",
    "tr": "⿹",
    "bl": "⿺",
}

# IDS character -> ASCII operator (reverse mapping)
IDS_TO_ASCII = {v: k for k, v in ASCII_TO_IDS.items()}

# IDS character -> SUR side
IDS_TO_SUR_SIDE = {v: k for k, v in SUR_SIDE_TO_IDS.items()}

# Operator arities (for IDS parsing)
IDS_ARITY = {
    "⿰": 2, "⿱": 2, "⿲": 3, "⿳": 3,
    "⿴": 2, "⿵": 2, "⿶": 2, "⿷": 2,
    "⿸": 2, "⿹": 2, "⿺": 2, "⿻": 2,
}

# All IDS operators
IDS_OPERATORS = set(IDS_ARITY.keys())

# =============================================================================
# AST Nodes
# =============================================================================

@dataclass
class LayoutNode:
    """Layout operator with children."""
    op: str  # ASCII name: LR, TB, SUR, etc.
    children: list  # list of ExprNode
    split: Optional[str] = None  # e.g., "4/8"
    side: Optional[str] = None  # for SUR: full, top, bot, etc.
    inset: Optional[int] = None  # for SUR

@dataclass
class TransformNode:
    """Transform operator wrapping a child."""
    op: str  # sc, sh, sk
    child: object  # ExprNode
    params: dict  # e.g., {"sx": 8, "sy": 8}

@dataclass
class RefNode:
    """Component or character reference."""
    name: str  # CJK char, pinyin, or component name

@dataclass
class StrokeNode:
    """Stroke expression (S(...)) - passed through unchanged."""
    raw: str  # Original S(...) text

# =============================================================================
# ASCII Parser (for expressions)
# =============================================================================

class AsciiExprParser:
    """Parse CSDL-ASCII expressions into AST."""

    LAYOUT_OPS = {"LR", "TB", "LR3", "TB3", "SUR", "OVR", "GRP", "GRID"}
    XFORM_OPS = {"sc", "sh", "sk"}
    SUR_SIDES = {"full", "tl", "tr", "top", "right", "left", "bot", "bl", "br"}

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def parse(self):
        """Parse a complete expression."""
        self.skip_ws()
        return self.parse_expr()

    def skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos] in " \t":
            self.pos += 1

    def peek(self, n=1) -> str:
        return self.text[self.pos:self.pos + n]

    def consume(self, n=1) -> str:
        result = self.text[self.pos:self.pos + n]
        self.pos += n
        return result

    def parse_expr(self):
        """Parse an expression: layout, transform, stroke, or reference."""
        self.skip_ws()

        # Check for layout operator
        for op in sorted(self.LAYOUT_OPS, key=len, reverse=True):
            if self.text[self.pos:].startswith(op + "("):
                return self.parse_layout(op)

        # Check for transform operator
        for op in self.XFORM_OPS:
            if self.text[self.pos:].startswith(op + "("):
                return self.parse_transform(op)

        # Check for stroke S(...)
        if self.text[self.pos:].startswith("S("):
            return self.parse_stroke()

        # Must be a reference
        return self.parse_ref()

    def parse_layout(self, op: str):
        """Parse LR(a, b), TB(a, b, 4/8), SUR(a, b, top), etc."""
        self.consume(len(op))  # consume operator name
        self.consume(1)  # consume (
        self.skip_ws()

        children = [self.parse_expr()]
        split = None
        side = None
        inset = None

        while True:
            self.skip_ws()
            if self.peek() == ")":
                self.consume(1)
                break
            if self.peek() == ",":
                self.consume(1)
                self.skip_ws()

                # Check if next is split ratio
                if re.match(r"\d+/\d+", self.text[self.pos:]):
                    m = re.match(r"\d+/\d+(?:/\d+)?", self.text[self.pos:])
                    split = m.group()
                    self.pos += len(split)
                    continue

                # Check if next is SUR side
                for s in sorted(self.SUR_SIDES, key=len, reverse=True):
                    if self.text[self.pos:].startswith(s):
                        # Make sure it's a complete token
                        end_pos = self.pos + len(s)
                        if end_pos >= len(self.text) or not self.text[end_pos].isalpha():
                            side = s
                            self.pos += len(s)
                            break
                if side:
                    continue

                # Check if next is inset (integer for SUR)
                if op == "SUR" and re.match(r"\d+", self.text[self.pos:]):
                    m = re.match(r"\d+", self.text[self.pos:])
                    inset = int(m.group())
                    self.pos += len(m.group())
                    continue

                # Otherwise, parse next child
                children.append(self.parse_expr())

        return LayoutNode(op, children, split, side, inset)

    def parse_transform(self, op: str):
        """Parse sc(expr, sx=8, sy=8), etc."""
        self.consume(len(op))  # consume operator name
        self.consume(1)  # consume (
        self.skip_ws()

        child = self.parse_expr()
        params = {}

        while True:
            self.skip_ws()
            if self.peek() == ")":
                self.consume(1)
                break
            if self.peek() == ",":
                self.consume(1)
                self.skip_ws()
                # Parse param=value
                m = re.match(r"([a-z]+)=(-?\d+)", self.text[self.pos:])
                if m:
                    params[m.group(1)] = int(m.group(2))
                    self.pos += len(m.group())

        return TransformNode(op, child, params)

    def parse_stroke(self):
        """Parse S(...) - capture entire expression."""
        start = self.pos
        depth = 0
        while self.pos < len(self.text):
            c = self.text[self.pos]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    self.pos += 1
                    return StrokeNode(self.text[start:self.pos])
            self.pos += 1
        return StrokeNode(self.text[start:self.pos])

    def parse_ref(self):
        """Parse a component reference (CJK char or pinyin name)."""
        self.skip_ws()
        start = self.pos

        # CJK character
        if self.pos < len(self.text):
            c = self.text[self.pos]
            if is_cjk(c):
                self.pos += 1
                # Check for variant tag
                while self.pos < len(self.text) and self.text[self.pos] == ".":
                    self.pos += 1
                    while self.pos < len(self.text) and self.text[self.pos].isalnum():
                        self.pos += 1
                return RefNode(self.text[start:self.pos])

        # Pinyin or component name
        while self.pos < len(self.text):
            c = self.text[self.pos]
            if c.isalnum() or c in ".-":
                self.pos += 1
            else:
                break

        name = self.text[start:self.pos]
        if not name:
            raise ValueError(f"Expected reference at position {self.pos}")
        return RefNode(name)


def is_cjk(c: str) -> bool:
    """Check if character is in CJK ranges."""
    cp = ord(c)
    return (
        0x3400 <= cp <= 0x9FFF or
        0xF900 <= cp <= 0xFAFF or
        0x20000 <= cp <= 0x2FA1F or
        0x30000 <= cp <= 0x323AF
    )


# =============================================================================
# CSDL-U Parser (IDS sequences)
# =============================================================================

class UExprParser:
    """Parse CSDL-U expressions (IDS prefix notation) into AST."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def parse(self):
        """Parse a complete expression."""
        return self.parse_expr()

    def peek(self) -> str:
        if self.pos >= len(self.text):
            return ""
        return self.text[self.pos]

    def consume(self) -> str:
        c = self.text[self.pos]
        self.pos += 1
        return c

    def parse_expr(self):
        """Parse an expression: IDS operator or reference."""
        c = self.peek()

        # IDS operator
        if c in IDS_OPERATORS:
            return self.parse_ids_op()

        # Transform annotation: ref@sc(...)
        # We need to parse ref first, then check for annotation
        ref = self.parse_ref()

        # Check for transform annotation
        if self.peek() == "@":
            self.consume()  # @
            return self.parse_transform_annotation(ref)

        return ref

    def parse_ids_op(self):
        """Parse IDS operator with children."""
        op_char = self.consume()
        arity = IDS_ARITY[op_char]
        children = []
        for _ in range(arity):
            children.append(self.parse_expr())

        # Check for split annotation
        split = None
        if self.peek() == ":":
            self.consume()  # :
            # Parse split ratio
            m = re.match(r"\d+/\d+(?:/\d+)?", self.text[self.pos:])
            if m:
                split = m.group()
                self.pos += len(split)

        # Convert IDS to ASCII operator
        if op_char in IDS_TO_ASCII:
            ascii_op = IDS_TO_ASCII[op_char]
            return LayoutNode(ascii_op, children, split)
        elif op_char in IDS_TO_SUR_SIDE:
            side = IDS_TO_SUR_SIDE[op_char]
            return LayoutNode("SUR", children, split, side)
        else:
            raise ValueError(f"Unknown IDS operator: {op_char}")

    def parse_transform_annotation(self, child):
        """Parse @sc(8,8), @sh(dx=2), etc."""
        # Get transform name
        m = re.match(r"(sc|sh|sk)\(", self.text[self.pos:])
        if not m:
            raise ValueError(f"Expected transform at position {self.pos}")
        op = m.group(1)
        self.pos += len(m.group())

        params = {}
        # Parse parameters
        while self.peek() != ")":
            # Could be named (sx=8) or positional for sc
            m = re.match(r"([a-z]+)=(-?\d+)", self.text[self.pos:])
            if m:
                params[m.group(1)] = int(m.group(2))
                self.pos += len(m.group())
            else:
                # Positional - for sc, first is sx, second is sy
                m = re.match(r"(-?\d+)", self.text[self.pos:])
                if m:
                    if op == "sc":
                        if "sx" not in params:
                            params["sx"] = int(m.group(1))
                        else:
                            params["sy"] = int(m.group(1))
                    elif op == "sh":
                        if "dx" not in params:
                            params["dx"] = int(m.group(1))
                        else:
                            params["dy"] = int(m.group(1))
                    elif op == "sk":
                        if "kx" not in params:
                            params["kx"] = int(m.group(1))
                        else:
                            params["ky"] = int(m.group(1))
                    self.pos += len(m.group())

            if self.peek() == ",":
                self.consume()

        self.consume()  # )
        return TransformNode(op, child, params)

    def parse_ref(self):
        """Parse a reference (CJK character, possibly with variant tag)."""
        if self.pos >= len(self.text):
            raise ValueError("Unexpected end of input")

        c = self.consume()
        name = c

        # Check for variant tag (lowercase ASCII only, not CJK)
        while self.peek() == ".":
            self.consume()  # .
            tag = ""
            while self.pos < len(self.text) and self.text[self.pos].isascii() and self.text[self.pos].isalnum():
                tag += self.consume()
            name += "." + tag

        return RefNode(name)


# =============================================================================
# AST to String Conversion
# =============================================================================

def ast_to_ascii(node) -> str:
    """Convert AST to CSDL-ASCII string."""
    if isinstance(node, RefNode):
        return node.name

    if isinstance(node, StrokeNode):
        return node.raw

    if isinstance(node, TransformNode):
        child_str = ast_to_ascii(node.child)
        param_parts = [f"{k}={v}" for k, v in node.params.items()]
        params_str = ", ".join(param_parts)
        if params_str:
            return f"{node.op}({child_str}, {params_str})"
        else:
            return f"{node.op}({child_str})"

    if isinstance(node, LayoutNode):
        children_str = ", ".join(ast_to_ascii(c) for c in node.children)
        parts = [children_str]

        if node.split:
            parts.append(node.split)

        if node.op == "SUR" and node.side:
            parts.append(node.side)
            if node.inset is not None:
                parts.append(str(node.inset))

        return f"{node.op}({', '.join(parts)})"

    raise ValueError(f"Unknown node type: {type(node)}")


def ast_to_u(node) -> str:
    """Convert AST to CSDL-U string."""
    if isinstance(node, RefNode):
        return node.name

    if isinstance(node, StrokeNode):
        # Strokes use same S() syntax in both profiles
        return node.raw

    if isinstance(node, TransformNode):
        child_str = ast_to_u(node.child)
        # Use @transform annotation
        if node.op == "sc":
            sx = node.params.get("sx", 12)
            sy = node.params.get("sy", 12)
            return f"{child_str}@sc({sx},{sy})"
        elif node.op == "sh":
            dx = node.params.get("dx", 0)
            dy = node.params.get("dy", 0)
            return f"{child_str}@sh({dx},{dy})"
        elif node.op == "sk":
            kx = node.params.get("kx", 0)
            ky = node.params.get("ky", 0)
            return f"{child_str}@sk({kx},{ky})"
        else:
            raise ValueError(f"Unknown transform: {node.op}")

    if isinstance(node, LayoutNode):
        # Convert children first
        children_str = "".join(ast_to_u(c) for c in node.children)

        # Get IDS operator
        if node.op == "SUR":
            side = node.side or "full"
            ids_op = SUR_SIDE_TO_IDS.get(side)
            if not ids_op:
                # Unsupported SUR variant - fall back to full
                ids_op = "⿴"
        elif node.op in ("GRP", "GRID"):
            # No IDS equivalent - leave as ASCII
            children_ascii = ", ".join(ast_to_ascii(c) for c in node.children)
            return f"{node.op}({children_ascii})"
        else:
            ids_op = ASCII_TO_IDS.get(node.op)
            if not ids_op:
                raise ValueError(f"Unknown operator: {node.op}")

        result = ids_op + children_str

        # Add split annotation if present
        if node.split:
            result += f":{node.split}"

        return result

    raise ValueError(f"Unknown node type: {type(node)}")


# =============================================================================
# Line-Level Conversion
# =============================================================================

def convert_line_to_u(line: str) -> str:
    """Convert a single line from CSDL-ASCII to CSDL-U."""
    line = line.rstrip("\n\r")

    # Preserve blank lines
    if not line.strip():
        return line

    # Preserve comments
    if line.lstrip().startswith("#"):
        return line

    # Preserve metadata lines
    if line.lstrip().startswith("@"):
        return line

    # Preserve stroke definitions and build:/close: lines
    if re.match(r"\s*(build:|close:|rad:|sc:|freq:|ortho:|x-)", line):
        return line

    # Preserve stroke def lines (s1 = S(...))
    if re.match(r"\s*[a-z][a-z0-9]*\s*=\s*S\(", line):
        return line

    # Character definition: 明 ming2 = LR(日, 月)
    # or: U+660E ming2 = LR(日, 月)
    # or: 小.scaled = sc(小, ...)  (component with variant tag)
    m = re.match(r"^(\s*)([\u3400-\u9fff\U00020000-\U0002fa1f](?:\.[a-z]+)*|U\+[0-9A-Fa-f]+)\s+([a-z]+[0-9][a-z0-9]*(?:\.[a-z]+)*)\s*=\s*(.+)$", line)
    if m:
        indent, char, pinyin, expr_str = m.groups()
        try:
            parser = AsciiExprParser(expr_str.strip())
            ast = parser.parse()
            u_expr = ast_to_u(ast)
            # CSDL-U drops pinyin, uses char directly
            return f"{indent}{char} = {u_expr}"
        except Exception:
            return line  # Fallback: return unchanged

    # Component definition with variant tag but no pinyin: 小.scaled = sc(...)
    m = re.match(r"^(\s*)([\u3400-\u9fff\U00020000-\U0002fa1f](?:\.[a-z]+)+)\s*=\s*(.+)$", line)
    if m:
        indent, comp_name, expr_str = m.groups()
        try:
            parser = AsciiExprParser(expr_str.strip())
            ast = parser.parse()
            u_expr = ast_to_u(ast)
            return f"{indent}{comp_name} = {u_expr}"
        except Exception:
            return line  # Fallback: return unchanged

    # Try parsing as standalone expression
    try:
        parser = AsciiExprParser(line.strip())
        ast = parser.parse()
        return ast_to_u(ast)
    except Exception:
        return line


def convert_line_to_ascii(line: str) -> str:
    """Convert a single line from CSDL-U to CSDL-ASCII."""
    line = line.rstrip("\n\r")

    # Preserve blank lines
    if not line.strip():
        return line

    # Preserve comments
    if line.lstrip().startswith("#"):
        return line

    # Preserve metadata lines
    if line.lstrip().startswith("@"):
        return line

    # Preserve stroke definitions and build:/close: lines
    if re.match(r"\s*(build:|close:|rad:|sc:|freq:|ortho:|x-)", line):
        return line

    # Preserve stroke def lines (s1 = S(...))
    if re.match(r"\s*[a-z][a-z0-9]*\s*=\s*S\(", line):
        return line

    # Character definition: 明 = ⿰日月
    m = re.match(r"^(\s*)([\u3400-\u9fff\U00020000-\U0002fa1f]|U\+[0-9A-Fa-f]+)\s*=\s*(.+)$", line)
    if m:
        indent, char, expr_str = m.groups()
        try:
            parser = UExprParser(expr_str.strip())
            ast = parser.parse()
            ascii_expr = ast_to_ascii(ast)
            # Note: We don't have pinyin in CSDL-U, so we can't restore it
            # Use character as placeholder
            return f"{indent}{char} = {ascii_expr}"
        except Exception:
            return line  # Fallback: return unchanged

    # Check if line contains IDS operators or transform annotations
    if any(op in line for op in IDS_OPERATORS) or re.search(r"@(sc|sh|sk)\(", line):
        try:
            parser = UExprParser(line.strip())
            ast = parser.parse()
            return ast_to_ascii(ast)
        except Exception:
            return line

    return line


# =============================================================================
# Public API
# =============================================================================

def ascii_to_u(text: str) -> str:
    """Convert CSDL-ASCII text to CSDL-U."""
    lines = text.split("\n")
    converted = [convert_line_to_u(line) for line in lines]
    return "\n".join(converted)


def u_to_ascii(text: str) -> str:
    """Convert CSDL-U text to CSDL-ASCII."""
    lines = text.split("\n")
    converted = [convert_line_to_ascii(line) for line in lines]
    return "\n".join(converted)


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert between CSDL-ASCII and CSDL-U profiles"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--to-u", action="store_true", help="Convert to CSDL-U")
    group.add_argument("--to-ascii", action="store_true", help="Convert to CSDL-ASCII")
    parser.add_argument("input", nargs="?", help="Input file (stdin if omitted)")

    args = parser.parse_args()

    # Read input
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    # Convert
    if args.to_u:
        result = ascii_to_u(text)
    else:
        result = u_to_ascii(text)

    # Output
    print(result, end="")


if __name__ == "__main__":
    main()
