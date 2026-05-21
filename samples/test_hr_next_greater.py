import pytest
import math
import os
import random
import re
import sys
from collections import defaultdict
from hr_next_greater import findNextGreaterElementsWithDistance

def test_normal_case_findNextGreaterElementsWithDistance():
    readings = [2, 5, 9, 3, 1, 12, 6, 8, 4]
    expected_result = [(12, 5), (12, 4), (12, 3), (6, 2), (12, 5), (8, 1), (8, 1), (8, 1), [-1, -1]]
    assert findNextGreaterElementsWithDistance(readings) == expected_result

def test_empty_list_findNextGreaterElementsWithDistance():
    readings = []
    try:
        findNextGreaterElementsWithDistance(readings)
        assert False
    except IndexError:
        assert True

def test_single_element_list_findNextGreaterElementsWithDistance():
    readings = [5]
    assert findNextGreaterElementsWithDistance(readings) == [[-1, -1]]

def test_no_greater_element_findNextGreaterElementsWithDistance():
    readings = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    expected_result = [[-1, -1]] * 10
    assert findNextGreaterElementsWithDistance(readings) == expected_result

def test_all_elements_greater_findNextGreaterElementsWithDistance():
    readings = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    expected_result = [(2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), [-1, -1]]
    assert findNextGreaterElementsWithDistance(readings) == expected_result

def test_equal_elements_findNextGreaterElementsWithDistance():
    readings = [5, 5, 5, 5, 5]
    expected_result = [[-1, -1]] * 5
    assert findNextGreaterElementsWithDistance(readings) == expected_result

def test_large_list_findNextGreaterElementsWithDistance():
    readings = [10] * 1000 + [11]
    expected_result = [[11, 1000]] * 1000 + [[-1, -1]]
    assert findNextGreaterElementsWithDistance(readings) == expected_result