#!/usr/bin/env python3
"""
IDS → CSDL transformer sketch.

Converts Ideographic Description Sequences to CSDL expressions.
Proof of concept for CSDL-lo8.
"""

# IDS operator → CSDL operator mapping
IDS_TO_CSDL = {
    '⿰': ('LR', 2),      # left-right
    '⿱': ('TB', 2),      # top-bottom
    '⿲': ('LR3', 3),     # left-middle-right
    '⿳': ('TB3', 3),     # top-middle-bottom
    '⿴': ('SUR', 2, 'full'),   # surround full
    '⿵': ('SUR', 2, 'top'),    # surround open bottom
    '⿶': ('SUR', 2, 'bot'),    # surround open top
    '⿷': ('SUR', 2, 'left'),   # surround open right
    '⿸': ('SUR', 2, 'tl'),     # surround top-left
    '⿹': ('SUR', 2, 'tr'),     # surround top-right
    '⿺': ('SUR', 2, 'bl'),     # surround bottom-left
    '⿻': ('OVR', 2),     # overlay
}

IDS_OPERATORS = set(IDS_TO_CSDL.keys())


def parse_ids(ids: str, pos: int = 0) -> tuple:
    """
    Recursive descent parser for IDS.
    Returns (tree, end_position).
    Tree is either a character or (operator, children...).
    """
    if pos >= len(ids):
        raise ValueError(f"Unexpected end of IDS: {ids}")

    char = ids[pos]

    if char in IDS_OPERATORS:
        op_info = IDS_TO_CSDL[char]
        op_name = op_info[0]
        arity = op_info[1]

        children = []
        current_pos = pos + 1
        for _ in range(arity):
            child, current_pos = parse_ids(ids, current_pos)
            children.append(child)

        if len(op_info) > 2:  # has side parameter (SUR)
            return ((op_name, op_info[2], tuple(children)), current_pos)
        else:
            return ((op_name, tuple(children)), current_pos)
    else:
        # leaf character
        return (char, pos + 1)


def tree_to_csdl(tree) -> str:
    """Convert parsed tree to CSDL expression string."""
    if isinstance(tree, str):
        return tree

    op = tree[0]

    if op == 'SUR':
        # (SUR, side, (outer, inner))
        side = tree[1]
        children = tree[2]
        outer = tree_to_csdl(children[0])
        inner = tree_to_csdl(children[1])
        return f"SUR({outer}, {inner}, {side})"
    else:
        # (OP, (children...))
        children = tree[1]
        args = ', '.join(tree_to_csdl(c) for c in children)
        return f"{op}({args})"


def ids_to_csdl(ids: str) -> str:
    """Convert IDS string to CSDL expression."""
    tree, end_pos = parse_ids(ids)
    if end_pos != len(ids):
        raise ValueError(f"Trailing characters in IDS: {ids[end_pos:]}")
    return tree_to_csdl(tree)


# Examples
if __name__ == '__main__':
    examples = [
        ('明', '⿰日月'),
        ('想', '⿱相心'),
        ('國', '⿴囗或'),
        ('謝', '⿰言⿱身寸'),
        ('樹', '⿰⿱木⿰又寸木'),  # complex nesting
        ('街', '⿲彳圭亍'),
        ('章', '⿱立早'),
        ('問', '⿵門口'),
        ('凶', '⿶凵㐅'),
        ('匠', '⿷匚斤'),
        ('病', '⿸疒丙'),
        ('氣', '⿹气米'),
        ('道', '⿺辶首'),
    ]

    print("IDS → CSDL examples:\n")
    for char, ids in examples:
        try:
            csdl = ids_to_csdl(ids)
            print(f"{char} {ids} → {csdl}")
        except Exception as e:
            print(f"{char} {ids} → ERROR: {e}")

    print("\n---\nAs CSDL definitions:\n")
    for char, ids in examples:
        try:
            csdl = ids_to_csdl(ids)
            print(f"{char} = {csdl}")
        except:
            pass
