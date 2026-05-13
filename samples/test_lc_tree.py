import pytest
from typing import Optional
from lc_tree import is_same, is_subtree

def test_normal_case_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1, Node(2), Node(3))
    q = Node(1, Node(2), Node(3))
    assert is_same(p, q) == True

def test_not_same_val_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1, Node(2), Node(3))
    q = Node(2, Node(2), Node(3))
    assert is_same(p, q) == False

def test_not_same_left_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1, Node(2), Node(3))
    q = Node(1, Node(4), Node(3))
    assert is_same(p, q) == False

def test_not_same_right_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1, Node(2), Node(3))
    q = Node(1, Node(2), Node(4))
    assert is_same(p, q) == False

def test_p_none_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = None
    q = Node(1)
    assert is_same(p, q) == False

def test_q_none_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1)
    q = None
    assert is_same(p, q) == False

def test_both_none_is_same():
    assert is_same(None, None) == True

def test_p_only_left_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1, Node(2))
    q = Node(1, Node(2))
    assert is_same(p, q) == True

def test_p_only_right_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1, None, Node(2))
    q = Node(1, None, Node(2))
    assert is_same(p, q) == True

def test_q_only_left_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1, Node(2), None)
    q = Node(1, Node(2), None)
    assert is_same(p, q) == True

def test_q_only_right_is_same():
    class Node:
        def __init__(self, val, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    p = Node(1, None, Node(2))
    q = Node(1, None, Node(2))
    assert is_same(p, q) == True

def test_normal_case_is_subtree():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    root = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    sub_root = TreeNode(4, TreeNode(1), TreeNode(2))
    assert is_subtree(root, sub_root) == True

def test_empty_root_is_subtree():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    root = None
    sub_root = TreeNode(4, TreeNode(1), TreeNode(2))
    assert is_subtree(root, sub_root) == False

def test_empty_sub_root_is_subtree():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    root = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    sub_root = None
    assert is_subtree(root, sub_root) == False

def test_single_node_root_is_subtree():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    root = TreeNode(3)
    sub_root = TreeNode(3)
    assert is_subtree(root, sub_root) == True

def test_single_node_sub_root_is_subtree():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    root = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    sub_root = TreeNode(4)
    assert is_subtree(root, sub_root) == True

def test_not_subtree_is_subtree():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    root = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    sub_root = TreeNode(6)
    assert is_subtree(root, sub_root) == False

def test_same_tree_is_subtree():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    root = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    sub_root = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    assert is_subtree(root, sub_root) == True

def test_is_same():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    def is_same(t1, t2):
        if not t1 and not t2:
            return True
        if not t1 or not t2:
            return False
        return t1.val == t2.val and is_same(t1.left, t2.left) and is_same(t1.right, t2.right)

    t1 = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    t2 = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    assert is_same(t1, t2) == True

def test_is_not_same():
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    def is_same(t1, t2):
        if not t1 and not t2:
            return True
        if not t1 or not t2:
            return False
        return t1.val == t2.val and is_same(t1.left, t2.left) and is_same(t1.right, t2.right)

    t1 = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
    t2 = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(6)), TreeNode(5))
    assert is_same(t1, t2) == False