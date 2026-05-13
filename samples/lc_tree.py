from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_same(p, q):
    if not p and not q:
        return True
    if not p or not q or p.val != q.val:
        return False
    return is_same(p.left, q.left) and is_same(p.right, q.right)


def is_subtree(root: Optional[TreeNode], sub_root: Optional[TreeNode]) -> bool:
    if not sub_root:
        return False
    if not root:
        return False
    if root.val == sub_root.val:
        if is_same(root, sub_root):
            return True
    return is_subtree(root.left, sub_root) or is_subtree(root.right, sub_root)
