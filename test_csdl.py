#!/usr/bin/env python3
"""Tests for CSDL Level 1 parser."""

import tempfile
import os
from csdl import parse_file, tokenize, Parser, STROKE_REGISTRY

# =============================================================================
# Test Fixtures
# =============================================================================

VALID_MINIMAL = """
@csdl 1.0

@comp 口
build: s1 s2 s3
s1 = S(shu [3,2] [3,10] 1)
s2 = S(heng-zhe [3,2] [9,2] [9,10] 1)
s3 = S(heng [3,10] [9,10] 1)
@end

明 ming2 = LR(口, 口)
"""

VALID_FULL = """
# CSDL Example File
@csdl 1.0
@ortho Hant

# Aliases
@alias kou3 = 口
@alias ri4 = 日
@alias yue4 = 月

# Components
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

@comp 相
build: from_expr
LR(日, 口)
@end

# Characters
U+660E ming2 = LR(日, 月) rad:72 sc:8
U+554F wen4 = SUR(口, 口) rad:30 sc:11
U+60F3 xiang3 = TB(相, 口) rad:61 sc:13
"""

VALID_ALL_LAYOUTS = """
@csdl 1.0

@comp 口
build: s1
s1 = S(heng [0,0] [12,12] 1)
@end

# All layout operators
明 ming2 = LR(口, 口)
想 xiang3 = TB(口, 口)
樹 shu4 = LR3(口, 口, 口)
草 cao3 = TB3(口, 口, 口)
國 guo2 = SUR(口, 口)
井 jing3 = OVR(口, 口)
器 qi4 = GRID(口, 口, 口, 口)
森 sen1 = GRP(口, 口, 口)

# With splits
侍 shi4 = LR(口, 口, 4/8)
艹 cao3 = TB(口, 口, 3/9)
湖 hu2 = LR3(口, 口, 口, 3/6/3)

# SUR with side
床 chuang2 = SUR(口, 口, tl)
氣 qi4 = SUR(口, 口, tr)
冤 yuan1 = SUR(口, 口, top)
句 ju4 = SUR(口, 口, right)
医 yi1 = SUR(口, 口, left)
凶 xiong1 = SUR(口, 口, bot)
道 dao4 = SUR(口, 口, bl)
建 jian4 = SUR(口, 口, br)
"""

VALID_TRANSFORMS = """
@csdl 1.0

@comp 口
build: s1
s1 = S(heng [0,0] [12,12] 1)
@end

# Transform operators
縮 suo1 = sc(口, sx=8, sy=8)
移 yi2 = sh(口, dx=2, dy=3)
斜 xie2 = sk(口, kx=1, ky=0)

# Nested
組 zu3 = sh(sc(口, sx=6, sy=6), dx=3, dy=3)
"""

VALID_GRID24 = """
@csdl 1.0

@comp 辶.bot /24
build: s1 s2
s1 = S(heng-zhe-zhe-pie [2,12] [8,12] [8,18] [14,18] [6,22] 1)
s2 = S(na [6,22] [22,16] 1)
@end
"""

VALID_ALL_STROKES = """
@csdl 1.0

# Test base strokes (12)
@comp base1
build: a b c d e f
a = S(heng [0,0] [12,0] 1)
b = S(shu [0,0] [0,12] 1)
c = S(pie [12,0] [0,12] 1)
d = S(na [0,0] [12,12] 1)
e = S(dian [0,0] [1,1] 1)
f = S(ti [0,12] [12,0] 1)
@end

@comp base2
build: a b c d e f
a = S(gou [0,0] [0,12] 1)
b = S(wan [0,0] [12,12] 1)
c = S(zhe [0,0] [6,6] 1)
d = S(xie [0,0] [12,12] 1)
e = S(wo [0,0] [12,12] 1)
f = S(quan [0,0] [6,12] [12,0] 1)
@end

# Test compound strokes
@comp compound1
build: a b c d
a = S(heng-zhe [0,0] [6,0] [6,12] 1)
b = S(shu-gou [0,0] [0,12] [6,6] 1)
c = S(heng-zhe-gou [0,0] [6,0] [6,12] [0,6] 1)
d = S(heng-zhe-zhe-zhe-gou [0,0] [2,0] [2,4] [4,4] [4,8] [0,8] 1)
@end
"""

VALID_CHAR_BLOCK = """
@csdl 1.0

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
"""

# Invalid test cases
INVALID_UNKNOWN_STROKE = """
@csdl 1.0
@comp 口
build: s1
s1 = S(fake-stroke [0,0] [12,12] 1)
@end
"""

INVALID_WRONG_POINTS = """
@csdl 1.0
@comp 口
build: s1
s1 = S(heng [0,0] [6,6] [12,12] 1)
@end
"""

INVALID_COORD_RANGE = """
@csdl 1.0
@comp 口
build: s1
s1 = S(heng [0,0] [15,15] 1)
@end
"""

INVALID_WIDTH = """
@csdl 1.0
@comp 口
build: s1
s1 = S(heng [0,0] [12,12] 5)
@end
"""

INVALID_INSET = """
@csdl 1.0
@comp 口
build: s1
s1 = S(heng [0,0] [12,12] 1)
@end
國 guo2 = SUR(口, 口, full, 10)
"""

INVALID_TPARAM = """
@csdl 1.0
@comp 口
build: s1
s1 = S(heng [0,0] [12,12] 1)
@end
縮 suo1 = sc(口, sx=30, sy=30)
"""

INVALID_GRP_ONE = """
@csdl 1.0
@comp 口
build: s1
s1 = S(heng [0,0] [12,12] 1)
@end
單 dan1 = GRP(口)
"""

INVALID_CYCLE = """
@csdl 1.0
@comp 甲
build: from_expr
LR(乙, 乙)
@end

@comp 乙
build: from_expr
TB(甲, 甲)
@end
"""

INVALID_DUPLICATE_COMP = """
@csdl 1.0
@comp 口
build: s1
s1 = S(heng [0,0] [12,12] 1)
@end

@comp 口
build: s1
s1 = S(shu [0,0] [0,12] 1)
@end
"""

INVALID_DUPLICATE_ALIAS = """
@csdl 1.0
@alias kou3 = 口
@alias kou3 = 囗
"""

INVALID_BUILD_MISMATCH = """
@csdl 1.0
@comp 口
build: s1 s2
s1 = S(heng [0,0] [12,12] 1)
@end
"""

INVALID_EXPR_WITH_STROKES = """
@csdl 1.0
@comp 口
build: from_expr
s1 = S(heng [0,0] [12,12] 1)
LR(日, 月)
@end
"""

INVALID_CLOSE_EXPR = """
@csdl 1.0
@comp 口
build: from_expr
close: s1
LR(日, 月)
@end
"""

INVALID_GRID24_EXPR = """
@csdl 1.0
@comp 口 /24
build: from_expr
LR(日, 月)
@end
"""


# =============================================================================
# Test Runner
# =============================================================================

def test_file(content: str, expect_valid: bool, name: str) -> bool:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csdl", delete=False, encoding="utf-8") as f:
        f.write(content)
        path = f.name

    try:
        valid, errors = parse_file(path)
        if valid == expect_valid:
            print(f"PASS: {name}")
            return True
        else:
            print(f"FAIL: {name} (expected {'valid' if expect_valid else 'invalid'}, got {'valid' if valid else 'invalid'})")
            if errors:
                for e in errors[:3]:
                    print(f"      {e}")
            return False
    finally:
        os.unlink(path)


def test_stroke_registry():
    """Verify stroke registry has exactly 38 strokes."""
    count = len(STROKE_REGISTRY)
    if count == 39:  # 38 standard + wan-quan
        print(f"PASS: stroke registry has {count} strokes (38 + wan-quan)")
        return True
    else:
        print(f"FAIL: stroke registry has {count} strokes, expected 39")
        return False


def main():
    passed = 0
    failed = 0

    tests = [
        # Valid cases
        (VALID_MINIMAL, True, "minimal valid file"),
        (VALID_FULL, True, "full example file"),
        (VALID_ALL_LAYOUTS, True, "all layout operators"),
        (VALID_TRANSFORMS, True, "transform operators"),
        (VALID_GRID24, True, "/24 grid mode"),
        (VALID_ALL_STROKES, True, "all stroke types"),
        (VALID_CHAR_BLOCK, True, "character block form"),

        # Invalid cases
        (INVALID_UNKNOWN_STROKE, False, "unknown stroke name"),
        (INVALID_WRONG_POINTS, False, "wrong point count"),
        (INVALID_COORD_RANGE, False, "coordinate out of range"),
        (INVALID_WIDTH, False, "invalid width"),
        (INVALID_INSET, False, "inset out of range"),
        (INVALID_TPARAM, False, "transform param out of range"),
        (INVALID_GRP_ONE, False, "GRP with one child"),
        (INVALID_CYCLE, False, "cyclic component reference"),
        (INVALID_DUPLICATE_COMP, False, "duplicate component"),
        (INVALID_DUPLICATE_ALIAS, False, "duplicate alias"),
        (INVALID_BUILD_MISMATCH, False, "build line mismatch"),
        (INVALID_EXPR_WITH_STROKES, False, "from_expr with strokes"),
        (INVALID_CLOSE_EXPR, False, "close in expr block"),
        (INVALID_GRID24_EXPR, False, "/24 with from_expr"),
    ]

    # Run stroke registry test
    if test_stroke_registry():
        passed += 1
    else:
        failed += 1

    # Run file tests
    for content, expect_valid, name in tests:
        if test_file(content, expect_valid, name):
            passed += 1
        else:
            failed += 1

    print(f"\n{passed}/{passed + failed} tests passed")
    return failed == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
