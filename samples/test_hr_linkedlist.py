import pytest
from unittest.mock import MagicMock, call
import math
import os
import random
import re
import sys
from hr_linkedlist import print_singly_linked_list, removeKthNodeFromEnd, SinglyLinkedListNode, SinglyLinkedList

def test_normal_insert_node():
    linked_list = SinglyLinkedList()
    linked_list.insert_node(1)
    assert linked_list.head.data == 1
    assert linked_list.tail.data == 1
    assert linked_list.head.next is None

def test_insert_multiple_nodes():
    linked_list = SinglyLinkedList()
    linked_list.insert_node(1)
    linked_list.insert_node(2)
    linked_list.insert_node(3)
    assert linked_list.head.data == 1
    assert linked_list.head.next.data == 2
    assert linked_list.tail.data == 3
    assert linked_list.tail.next is None

def test_insert_node_with_empty_list(monkeypatch):
    mock_node = MagicMock()
    monkeypatch.setattr('hr_linkedlist.SinglyLinkedListNode', lambda x: mock_node)
    linked_list = SinglyLinkedList()
    linked_list.insert_node(1)
    assert linked_list.head is mock_node
    assert linked_list.tail is mock_node

def test_insert_node_with_single_element_list(monkeypatch):
    mock_node = MagicMock()
    monkeypatch.setattr('hr_linkedlist.SinglyLinkedListNode', lambda x: mock_node)
    linked_list = SinglyLinkedList()
    linked_list.head = SinglyLinkedListNode(1)
    linked_list.tail = linked_list.head
    linked_list.insert_node(2)
    assert linked_list.head.data == 1
    assert linked_list.head.next is mock_node
    assert linked_list.tail is mock_node

def test_insert_node_with_multiple_elements_list(monkeypatch):
    mock_node = MagicMock()
    monkeypatch.setattr('hr_linkedlist.SinglyLinkedListNode', lambda x: mock_node)
    linked_list = SinglyLinkedList()
    linked_list.head = SinglyLinkedListNode(1)
    linked_list.tail = SinglyLinkedListNode(2)
    linked_list.head.next = linked_list.tail
    linked_list.insert_node(3)
    assert linked_list.head.data == 1
    assert linked_list.head.next.data == 2
    assert linked_list.tail is mock_node

def test_normal_print_singly_linked_list():
    node = SinglyLinkedListNode(1)
    node.next = SinglyLinkedListNode(2)
    node.next.next = SinglyLinkedListNode(3)
    import io
    import sys
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    print_singly_linked_list(node, sep=' ')
    sys.stdout = sys.__stdout__
    assert capturedOutput.getvalue() == '1 2 3'

def test_empty_print_singly_linked_list():
    node = None
    import io
    import sys
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    print_singly_linked_list(node, sep=' ')
    sys.stdout = sys.__stdout__
    assert capturedOutput.getvalue() == ''

def test_single_node_print_singly_linked_list():
    node = SinglyLinkedListNode(1)
    import io
    import sys
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    print_singly_linked_list(node, sep=' ')
    sys.stdout = sys.__stdout__
    assert capturedOutput.getvalue() == '1'

def test_no_sep_print_singly_linked_list():
    node = SinglyLinkedListNode(1)
    node.next = SinglyLinkedListNode(2)
    node.next.next = SinglyLinkedListNode(3)
    import io
    import sys
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    print_singly_linked_list(node, sep='')
    sys.stdout = sys.__stdout__
    assert capturedOutput.getvalue() == '123'

def test_custom_sep_print_singly_linked_list():
    node = SinglyLinkedListNode(1)
    node.next = SinglyLinkedListNode(2)
    node.next.next = SinglyLinkedListNode(3)
    import io
    import sys
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    print_singly_linked_list(node, sep='-')
    sys.stdout = sys.__stdout__
    assert capturedOutput.getvalue() == '1-2-3'

def test_normal_case_removeKthNodeFromEnd():
    head = SinglyLinkedListNode(1)
    head.next = SinglyLinkedListNode(2)
    head.next.next = SinglyLinkedListNode(3)
    head.next.next.next = SinglyLinkedListNode(4)
    head.next.next.next.next = SinglyLinkedListNode(5)
    result = removeKthNodeFromEnd(head, 2)
    assert result.data == 1
    assert result.next.data == 2
    assert result.next.next.data == 3
    assert result.next.next.next.data == 4
    assert result.next.next.next.next is None

def test_k_is_1_removeKthNodeFromEnd():
    head = SinglyLinkedListNode(1)
    head.next = SinglyLinkedListNode(2)
    head.next.next = SinglyLinkedListNode(3)
    result = removeKthNodeFromEnd(head, 1)
    assert result.data == 1
    assert result.next.data == 2
    assert result.next.next is None

def test_k_is_equal_to_length_removeKthNodeFromEnd():
    head = SinglyLinkedListNode(1)
    head.next = SinglyLinkedListNode(2)
    head.next.next = SinglyLinkedListNode(3)
    result = removeKthNodeFromEnd(head, 3)
    assert result.data == 2
    assert result.next.data == 3
    assert result.next.next is None

def test_k_is_greater_than_length_removeKthNodeFromEnd():
    head = SinglyLinkedListNode(1)
    head.next = SinglyLinkedListNode(2)
    head.next.next = SinglyLinkedListNode(3)
    result = removeKthNodeFromEnd(head, 4)
    assert result.data == 1
    assert result.next.data == 2
    assert result.next.next.data == 3
    assert result.next.next.next is None

def test_empty_list_removeKthNodeFromEnd():
    result = removeKthNodeFromEnd(None, 1)
    assert result is None

def test_single_node_list_removeKthNodeFromEnd():
    head = SinglyLinkedListNode(1)
    result = removeKthNodeFromEnd(head, 1)
    assert result is None