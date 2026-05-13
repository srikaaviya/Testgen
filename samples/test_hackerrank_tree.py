import pytest

from hackerrank_tree import insert, has_different_structure, TreeNode

def test_normal_insert():
    root = None
    val = 5
    result = insert(root, val)
    assert result.val == 5
    assert result.left is None
    assert result.right is None

def test_left_insert():
    root = TreeNode(5)
    val = 3
    result = insert(root, val)
    assert result.val == 5
    assert result.left.val == 3
    assert result.left.left is None
    assert result.left.right is None
    assert result.right is None

def test_right_insert():
    root = TreeNode(5)
    val = 7
    result = insert(root, val)
    assert result.val == 5
    assert result.left is None
    assert result.right.val == 7
    assert result.right.left is None
    assert result.right.right is None

def test_equal_insert():
    root = TreeNode(5)
    val = 5
    result = insert(root, val)
    assert result.val == 5
    assert result.left is None
    assert result.right.val == 5
    assert result.right.left is None
    assert result.right.right is None

def test_insert_none_root():
    root = None
    val = 0
    result = insert(root, val)
    assert result.val == 0
    assert result.left is None
    assert result.right is None

def test_insert_negative_val():
    root = TreeNode(5)
    val = -3
    result = insert(root, val)
    assert result.val == 5
    assert result.left.val == -3
    assert result.left.left is None
    assert result.left.right is None
    assert result.right is None

def test_insert_float_val():
    root = TreeNode(5)
    val = 3.5
    result = insert(root, val)
    assert result.val == 5
    assert result.left.val == 3.5
    assert result.left.left is None
    assert result.left.right is None
    assert result.right is None

def test_insert_duplicate_val():
    root = TreeNode(5)
    val = 5
    result = insert(root, val)
    assert result.val == 5
    assert result.left is None
    assert result.right.val == 5
    assert result.right.left is None
    assert result.right.right is None

def test_normal_case_has_different_structure():
    class TreeNode:
        def __init__(self, x):
            self.val = x
            self.left = None
            self.right = None

    p = TreeNode(1)
    p.left = TreeNode(2)
    p.right = TreeNode(3)
    q = TreeNode(1)
    q.left = TreeNode(2)
    q.right = TreeNode(3)
    assert has_different_structure(p, q) == False

def test_empty_tree_has_different_structure():
    class TreeNode:
        def __init__(self, x):
            self.val = x
            self.left = None
            self.right = None

    p = None
    q = None
    assert has_different_structure(p, q) == False

def test_one_empty_tree_has_different_structure():
    class TreeNode:
        def __init__(self, x):
            self.val = x
            self.left = None
            self.right = None

    p = TreeNode(1)
    q = None
    assert has_different_structure(p, q) == True

def test_different_structure_has_different_structure():
    class TreeNode:
        def __init__(self, x):
            self.val = x
            self.left = None
            self.right = None

    p = TreeNode(1)
    p.left = TreeNode(2)
    q = TreeNode(1)
    q.right = TreeNode(3)
    assert has_different_structure(p, q) == True