#!/usr/bin/env python3
"""
Tests for CSDL Profile Converter

Tests round-trip conversion between CSDL-ASCII and CSDL-U profiles.
"""

import unittest
from csdl_convert import (
    ascii_to_u, u_to_ascii,
    AsciiExprParser, UExprParser,
    ast_to_ascii, ast_to_u,
    LayoutNode, RefNode, TransformNode,
)


class TestAsciiToU(unittest.TestCase):
    """Test CSDL-ASCII to CSDL-U conversion."""

    def test_simple_lr(self):
        """LR(日, 月) -> ⿰日月"""
        result = ascii_to_u("LR(日, 月)")
        self.assertEqual(result, "⿰日月")

    def test_simple_tb(self):
        """TB(木, 本) -> ⿱木本"""
        result = ascii_to_u("TB(木, 本)")
        self.assertEqual(result, "⿱木本")

    def test_lr3(self):
        """LR3(氵, 木, 夕) -> ⿲氵木夕"""
        result = ascii_to_u("LR3(氵, 木, 夕)")
        self.assertEqual(result, "⿲氵木夕")

    def test_tb3(self):
        """TB3(日, 木, 火) -> ⿳日木火"""
        result = ascii_to_u("TB3(日, 木, 火)")
        self.assertEqual(result, "⿳日木火")

    def test_ovr(self):
        """OVR(十, 口) -> ⿻十口"""
        result = ascii_to_u("OVR(十, 口)")
        self.assertEqual(result, "⿻十口")

    def test_sur_full(self):
        """SUR(囗, 玉, full) -> ⿴囗玉"""
        result = ascii_to_u("SUR(囗, 玉, full)")
        self.assertEqual(result, "⿴囗玉")

    def test_sur_top(self):
        """SUR(冂, 入, top) -> ⿵冂入"""
        result = ascii_to_u("SUR(冂, 入, top)")
        self.assertEqual(result, "⿵冂入")

    def test_sur_bot(self):
        """SUR(凵, 山, bot) -> ⿶凵山"""
        result = ascii_to_u("SUR(凵, 山, bot)")
        self.assertEqual(result, "⿶凵山")

    def test_sur_left(self):
        """SUR(匚, 矢, left) -> ⿷匚矢"""
        result = ascii_to_u("SUR(匚, 矢, left)")
        self.assertEqual(result, "⿷匚矢")

    def test_sur_tl(self):
        """SUR(厂, 干, tl) -> ⿸厂干"""
        result = ascii_to_u("SUR(厂, 干, tl)")
        self.assertEqual(result, "⿸厂干")

    def test_sur_tr(self):
        """SUR(气, 米, tr) -> ⿹气米"""
        result = ascii_to_u("SUR(气, 米, tr)")
        self.assertEqual(result, "⿹气米")

    def test_sur_bl(self):
        """SUR(辶, 首, bl) -> ⿺辶首"""
        result = ascii_to_u("SUR(辶, 首, bl)")
        self.assertEqual(result, "⿺辶首")

    def test_nested(self):
        """TB(木, LR(木, 木)) -> ⿱木⿰木木"""
        result = ascii_to_u("TB(木, LR(木, 木))")
        self.assertEqual(result, "⿱木⿰木木")

    def test_deeply_nested(self):
        """LR(氵, TB(艹, LR(日, 月))) -> ⿰氵⿱艹⿰日月"""
        result = ascii_to_u("LR(氵, TB(艹, LR(日, 月)))")
        self.assertEqual(result, "⿰氵⿱艹⿰日月")

    def test_with_split(self):
        """LR(日, 月, 4/8) -> ⿰日月:4/8"""
        result = ascii_to_u("LR(日, 月, 4/8)")
        self.assertEqual(result, "⿰日月:4/8")

    def test_with_transform(self):
        """sc(日, sx=8, sy=8) -> 日@sc(8,8)"""
        result = ascii_to_u("sc(日, sx=8, sy=8)")
        self.assertEqual(result, "日@sc(8,8)")

    def test_char_definition(self):
        """Character definition line."""
        result = ascii_to_u("明 ming2 = LR(日, 月)")
        self.assertEqual(result, "明 = ⿰日月")

    def test_preserve_comment(self):
        """Comments are preserved."""
        result = ascii_to_u("# This is a comment")
        self.assertEqual(result, "# This is a comment")

    def test_preserve_metadata(self):
        """Metadata lines are preserved."""
        result = ascii_to_u("@csdl 1.0")
        self.assertEqual(result, "@csdl 1.0")

    def test_preserve_blank(self):
        """Blank lines are preserved."""
        result = ascii_to_u("")
        self.assertEqual(result, "")

    def test_variant_tag(self):
        """Component with variant tag."""
        result = ascii_to_u("LR(心.left, 口)")
        self.assertEqual(result, "⿰心.left口")


class TestUToAscii(unittest.TestCase):
    """Test CSDL-U to CSDL-ASCII conversion."""

    def test_simple_lr(self):
        """⿰日月 -> LR(日, 月)"""
        result = u_to_ascii("⿰日月")
        self.assertEqual(result, "LR(日, 月)")

    def test_simple_tb(self):
        """⿱木本 -> TB(木, 本)"""
        result = u_to_ascii("⿱木本")
        self.assertEqual(result, "TB(木, 本)")

    def test_lr3(self):
        """⿲氵木夕 -> LR3(氵, 木, 夕)"""
        result = u_to_ascii("⿲氵木夕")
        self.assertEqual(result, "LR3(氵, 木, 夕)")

    def test_tb3(self):
        """⿳日木火 -> TB3(日, 木, 火)"""
        result = u_to_ascii("⿳日木火")
        self.assertEqual(result, "TB3(日, 木, 火)")

    def test_ovr(self):
        """⿻十口 -> OVR(十, 口)"""
        result = u_to_ascii("⿻十口")
        self.assertEqual(result, "OVR(十, 口)")

    def test_sur_full(self):
        """⿴囗玉 -> SUR(囗, 玉, full)"""
        result = u_to_ascii("⿴囗玉")
        self.assertEqual(result, "SUR(囗, 玉, full)")

    def test_sur_top(self):
        """⿵冂入 -> SUR(冂, 入, top)"""
        result = u_to_ascii("⿵冂入")
        self.assertEqual(result, "SUR(冂, 入, top)")

    def test_sur_bot(self):
        """⿶凵山 -> SUR(凵, 山, bot)"""
        result = u_to_ascii("⿶凵山")
        self.assertEqual(result, "SUR(凵, 山, bot)")

    def test_sur_left(self):
        """⿷匚矢 -> SUR(匚, 矢, left)"""
        result = u_to_ascii("⿷匚矢")
        self.assertEqual(result, "SUR(匚, 矢, left)")

    def test_sur_tl(self):
        """⿸厂干 -> SUR(厂, 干, tl)"""
        result = u_to_ascii("⿸厂干")
        self.assertEqual(result, "SUR(厂, 干, tl)")

    def test_sur_tr(self):
        """⿹气米 -> SUR(气, 米, tr)"""
        result = u_to_ascii("⿹气米")
        self.assertEqual(result, "SUR(气, 米, tr)")

    def test_sur_bl(self):
        """⿺辶首 -> SUR(辶, 首, bl)"""
        result = u_to_ascii("⿺辶首")
        self.assertEqual(result, "SUR(辶, 首, bl)")

    def test_nested(self):
        """⿱木⿰木木 -> TB(木, LR(木, 木))"""
        result = u_to_ascii("⿱木⿰木木")
        self.assertEqual(result, "TB(木, LR(木, 木))")

    def test_deeply_nested(self):
        """⿰氵⿱艹⿰日月 -> LR(氵, TB(艹, LR(日, 月)))"""
        result = u_to_ascii("⿰氵⿱艹⿰日月")
        self.assertEqual(result, "LR(氵, TB(艹, LR(日, 月)))")

    def test_with_split(self):
        """⿰日月:4/8 -> LR(日, 月, 4/8)"""
        result = u_to_ascii("⿰日月:4/8")
        self.assertEqual(result, "LR(日, 月, 4/8)")

    def test_char_definition(self):
        """Character definition line."""
        result = u_to_ascii("明 = ⿰日月")
        self.assertEqual(result, "明 = LR(日, 月)")

    def test_preserve_comment(self):
        """Comments are preserved."""
        result = u_to_ascii("# This is a comment")
        self.assertEqual(result, "# This is a comment")

    def test_variant_tag(self):
        """Component with variant tag."""
        result = u_to_ascii("⿰心.left口")
        self.assertEqual(result, "LR(心.left, 口)")


class TestRoundTrip(unittest.TestCase):
    """Test round-trip conversion preserves semantics."""

    def assertRoundTrip(self, ascii_expr: str, u_expr: str = None):
        """Assert that ASCII -> U -> ASCII preserves structure."""
        u_result = ascii_to_u(ascii_expr)
        if u_expr:
            self.assertEqual(u_result, u_expr)
        # Round trip
        ascii_result = u_to_ascii(u_result)
        # Parse both to compare semantically
        orig_ast = AsciiExprParser(ascii_expr).parse()
        round_ast = AsciiExprParser(ascii_result).parse()
        self.assertEqual(type(orig_ast), type(round_ast))

    def test_roundtrip_lr(self):
        self.assertRoundTrip("LR(日, 月)", "⿰日月")

    def test_roundtrip_tb(self):
        self.assertRoundTrip("TB(木, 本)", "⿱木本")

    def test_roundtrip_transform(self):
        """Transform sc() round-trips correctly."""
        ascii_expr = "sc(日, sx=8, sy=10)"
        u_expr = ascii_to_u(ascii_expr)
        self.assertEqual(u_expr, "日@sc(8,10)")
        back = u_to_ascii(u_expr)
        self.assertEqual(back, "sc(日, sx=8, sy=10)")

    def test_roundtrip_nested(self):
        self.assertRoundTrip("TB(木, LR(木, 木))", "⿱木⿰木木")

    def test_roundtrip_sur_full(self):
        self.assertRoundTrip("SUR(囗, 玉, full)", "⿴囗玉")

    def test_roundtrip_sur_tl(self):
        self.assertRoundTrip("SUR(厂, 干, tl)", "⿸厂干")

    def test_roundtrip_with_split(self):
        self.assertRoundTrip("LR(日, 月, 4/8)", "⿰日月:4/8")


class TestMultiLine(unittest.TestCase):
    """Test multi-line file conversion."""

    def test_file_conversion(self):
        """Test converting a multi-line CSDL file."""
        ascii_text = """@csdl 1.0
@ortho Hani

# Basic characters
日 ri4 = S(heng[0,0][12,0])
月 yue4 = S(shu[0,0][0,12])

# Compound characters
明 ming2 = LR(日, 月)
森 sen1 = TB(木, LR(木, 木))
"""
        u_text = ascii_to_u(ascii_text)

        # Check key conversions
        self.assertIn("明 = ⿰日月", u_text)
        self.assertIn("森 = ⿱木⿰木木", u_text)

        # Check preserved elements
        self.assertIn("@csdl 1.0", u_text)
        self.assertIn("@ortho Hani", u_text)
        self.assertIn("# Basic characters", u_text)

    def test_grp_preserved(self):
        """GRP operator has no IDS equivalent, falls back."""
        result = ascii_to_u("GRP(a, b, c)")
        self.assertIn("GRP", result)

    def test_grid_preserved(self):
        """GRID operator has no IDS equivalent, falls back."""
        result = ascii_to_u("GRID(a, b, c, d)")
        self.assertIn("GRID", result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_component_variant_def(self):
        """Component with variant tag definition."""
        result = ascii_to_u("小.scaled = sc(小, sx=8, sy=8)")
        self.assertEqual(result, "小.scaled = 小@sc(8,8)")

    def test_pinyin_ref(self):
        """Pinyin references work."""
        result = ascii_to_u("LR(ri4, yue4)")
        self.assertEqual(result, "⿰ri4yue4")

    def test_mixed_ref(self):
        """Mixed CJK and pinyin refs."""
        result = ascii_to_u("LR(日, yue4)")
        self.assertEqual(result, "⿰日yue4")

    def test_three_part_split(self):
        """Three-part split for LR3/TB3."""
        result = ascii_to_u("LR3(a, b, c, 2/6/4)")
        self.assertEqual(result, "⿲abc:2/6/4")


if __name__ == "__main__":
    unittest.main()
