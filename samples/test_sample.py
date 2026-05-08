import pytest
from tests_projects.Testgen.samples.sample import add, divide

def test_normal_add():
    assert add(1, 2) == 3

def test_negative_add():
    assert add(-1, -2) == -3

def test_mixed_add():
    assert add(-1, 2) == 1

def test_zero_add():
    assert add(0, 0) == 0

def test_float_add():
    assert add(1.5, 2.5) == 4.0

def test_non_numeric_add():
    try:
        add("a", 2)
        assert False
    except TypeError:
        assert True

def test_complex_add():
    assert add(1 + 2j, 2 + 3j) == 3 + 5j

def test_large_add():
    assert add(1000000, 2000000) == 3000000

def test_edge_case_add():
    assert add(-2**31, 2**31 - 1) == -1

def test_type_error_add():
    try:
        add(None, 2)
        assert False
    except TypeError:
        assert True

def test_repr_add():
    assert repr(add(1, 2)) == repr(3)

def test_normal_case_divide():
    assert divide(10, 2) == 5

def test_divide_by_one_divide():
    assert divide(10, 1) == 10

def test_divide_zero_divide():
    with pytest.raises(ValueError) as e:
        divide(10, 0)
    assert repr(e.value) == repr(ValueError("Cannot divide by zero"))

def test_negative_numbers_divide():
    assert divide(-10, 2) == -5
    assert divide(10, -2) == -5
    assert divide(-10, -2) == 5

def test_float_numbers_divide():
    assert divide(10.5, 2) == 5.25
    assert divide(10, 2.5) == 4.0
    assert divide(10.5, 2.5) == 4.2

def test_large_numbers_divide():
    assert divide(1000000, 2) == 500000
    assert divide(1000000, 1000000) == 1

def test_invalid_input_divide():
    with pytest.raises(TypeError) as e:
        divide("10", 2)
    with pytest.raises(TypeError) as e:
        divide(10, "2") 
    with pytest.raises(TypeError) as e:
        divide([10], 2) 
    with pytest.raises(TypeError) as e:
        divide(10, [2])