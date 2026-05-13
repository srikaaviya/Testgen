class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def insert(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root


def has_different_structure(p, q):
    if not p and not q:
        return False   # both empty — same structure → return False
    if not p or not q:
        return True    # different structure → return True
    return has_different_structure(p.left, q.left) and has_different_structure(p.right, q.right)


