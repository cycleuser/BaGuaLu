---
name: test-generator
description: Generate comprehensive unit tests and integration tests for code. Use when users want to add tests, improve test coverage, or create test suites. Supports pytest, unittest, Jest, and other testing frameworks.
version: "1.0.0"
allowed-tools:
  - read
  - write
  - bash
---

# Test Generator Skill

## Overview

Automated test generation skill for BaGuaLu agents. Creates comprehensive unit tests, integration tests, and test fixtures.

## Capabilities

- Generate unit tests for functions and classes
- Create integration tests for APIs and workflows
- Generate test fixtures and mocks
- Calculate and improve test coverage
- Support multiple testing frameworks
- Generate parameterized tests

## Workflow

### Step 1: Analyze Code

1. Read the source code
2. Identify functions, classes, and methods
3. Understand dependencies and side effects
4. Identify edge cases and error paths

### Step 2: Generate Tests

#### Test Structure

```python
"""
Tests for [module_name]
"""

import pytest
from [module] import [function]


class Test[FunctionName]:
    """Test suite for [function_name]"""
    
    def test_normal_case(self):
        """Test normal operation"""
        # Arrange
        input_data = ...
        expected = ...
        
        # Act
        result = function_name(input_data)
        
        # Assert
        assert result == expected
    
    def test_edge_case(self):
        """Test edge case: [description]"""
        ...
    
    def test_error_case(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            function_name(invalid_input)
```

### Step 3: Coverage Analysis

```bash
pytest --cov=[module] --cov-report=term-missing
```

## Test Types

### Unit Tests

- Test individual functions/methods in isolation
- Mock external dependencies
- Fast execution
- Focus on business logic

### Integration Tests

- Test component interactions
- Use real dependencies (database, API)
- Slower execution
- Focus on data flow

### Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("input1", "expected1"),
    ("input2", "expected2"),
    ("input3", "expected3"),
])
def test_multiple_cases(input, expected):
    assert function(input) == expected
```

## Test Patterns

### Arrange-Act-Assert (AAA)

```python
def test_example():
    # Arrange
    data = [1, 2, 3]
    
    # Act
    result = sum(data)
    
    # Assert
    assert result == 6
```

### Given-When-Then (BDD)

```python
def test_user_creation():
    # Given
    user_data = {"name": "John", "email": "john@example.com"}
    
    # When
    user = create_user(user_data)
    
    # Then
    assert user.name == "John"
    assert user.email == "john@example.com"
```

### Mock External Dependencies

```python
from unittest.mock import Mock, patch

@patch('module.external_api_call')
def test_with_mock(mock_api):
    mock_api.return_value = {"status": "ok"}
    
    result = function_that_calls_api()
    
    assert result.status == "ok"
    mock_api.assert_called_once()
```

## Coverage Goals

- **Lines**: 80%+ for production code
- **Branches**: 70%+ for critical paths
- **Functions**: 90%+ for public APIs

## Test File Naming

```
source_file.py → test_source_file.py
module/ → tests/test_module/
```

## Example Output

### Input: calculator.py

```python
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Output: test_calculator.py

```python
"""Tests for calculator module."""

import pytest
from calculator import add, divide


class TestAdd:
    """Test suite for add function."""
    
    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, 3),
        (-1, 1, 0),
        (0, 0, 0),
        (100, 200, 300),
    ])
    def test_add_normal_cases(self, a, b, expected):
        """Test addition with various inputs."""
        assert add(a, b) == expected
    
    def test_add_floats(self):
        """Test addition with floating point numbers."""
        result = add(0.1, 0.2)
        assert abs(result - 0.3) < 1e-9


class TestDivide:
    """Test suite for divide function."""
    
    def test_divide_normal(self):
        """Test normal division."""
        assert divide(10, 2) == 5.0
    
    def test_divide_negative(self):
        """Test division with negative numbers."""
        assert divide(-10, 2) == -5.0
    
    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)
    
    @pytest.mark.parametrize("a,b,expected", [
        (10, 3, 10/3),
        (1, 3, 1/3),
        (0, 5, 0),
    ])
    def test_divide_various(self, a, b, expected):
        """Test division with various inputs."""
        assert divide(a, b) == expected
```

## Framework Support

### Python

- **pytest** (recommended): Rich features, simple syntax
- **unittest**: Built-in, class-based tests

### JavaScript/TypeScript

- **Jest**: Zero config, snapshot testing
- **Mocha + Chai**: Flexible, assertion libraries

### Go

- **testing** package: Built-in, table-driven tests

### Rust

- **cargo test**: Built-in, assertion macros

## Best Practices

1. **One concept per test**: Each test should verify one thing
2. **Descriptive names**: Test names should explain what they test
3. **Independent tests**: Tests should not depend on each other
4. **Repeatable**: Same test should always produce same result
5. **Fast**: Unit tests should be quick to run
6. **Readable**: Tests are documentation too

## Notes

- Generate tests that would catch real bugs
- Include both positive and negative test cases
- Test boundary conditions
- Mock external dependencies for unit tests
- Use fixtures for common setup
- Aim for high coverage but prioritize critical paths