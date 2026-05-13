import pytest

from hr_linkedlist import removeKthFromEnd

def test_normal_case_removeKthFromEnd():
    class ListNode:
        def __init__(self, x):
            self.val = x
            self.next = None

    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    head.next.next.next = ListNode(4)
    head.next.next.next.next = ListNode(5)
    result = removeKthFromEnd(head, 2)
    expected = [1, 2, 3, 5]
    current = result
    for val in expected:
        assert current.val == val
        current = current.next
    assert current is None

def test_edge_case_k_equals_0_removeKthFromEnd():
    class ListNode:
        def __init__(self, x):
            self.val = x
            self.next = None

    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    result = removeKthFromEnd(head, 0)
    expected = [1, 2, 3]
    current = result
    for val in expected:
        assert current.val == val
        current = current.next
    assert current is None

def test_edge_case_k_equals_n_removeKthFromEnd():
    class ListNode:
        def __init__(self, x):
            self.val = x
            self.next = None

    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    result = removeKthFromEnd(head, 3)
    expected = [2, 3]
    current = result
    for val in expected:
        assert current.val == val
        current = current.next
    assert current is None

def test_edge_case_k_greater_than_n_removeKthFromEnd():
    class ListNode:
        def __init__(self, x):
            self.val = x
            self.next = None

    head = ListNode(1)
    head.next = ListNode(2)
    head.next.next = ListNode(3)
    result = removeKthFromEnd(head, 4)
    expected = [1, 2, 3]
    current = result
    for val in expected:
        assert current.val == val
        current = current.next
    assert current is None

def test_empty_list_removeKthFromEnd():
    class ListNode:
        def __init__(self, x):
            self.val = x
            self.next = None

    head = None
    result = removeKthFromEnd(head, 1)
    assert result is None