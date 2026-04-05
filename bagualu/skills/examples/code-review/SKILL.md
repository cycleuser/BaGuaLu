---
name: code-review
description: Review code for quality, security, performance, and best practices. Use when users request code review, want feedback on code quality, need security analysis, or want performance optimization suggestions. Supports Python, JavaScript, TypeScript, Go, Rust, and more.
version: "1.0.0"
allowed-tools:
  - read
  - grep
  - glob
---

# Code Review Skill

## Overview

Comprehensive code review skill for BaGuaLu agents. Analyzes code quality, security, performance, and adherence to best practices.

## Capabilities

- Code quality analysis (complexity, maintainability, readability)
- Security vulnerability detection
- Performance optimization suggestions
- Best practices verification
- Style guide compliance
- Documentation coverage

## Review Process

### Step 1: Understand Context

Ask the user:
1. What is the codebase/project about?
2. Any specific areas of concern? (security, performance, architecture)
3. Target quality level? (production-ready, MVP, prototype)
4. Any specific standards to follow? (PEP8, ESLint, etc.)

### Step 2: Code Analysis

#### Quality Checks

- **Complexity**: Cyclomatic complexity, nesting depth, function length
- **Maintainability**: Code duplication, coupling, cohesion
- **Readability**: Naming conventions, comments, documentation

#### Security Checks

- **Injection vulnerabilities**: SQL, XSS, command injection
- **Authentication/Authorization**: Weak passwords, insecure sessions
- **Data validation**: Input sanitization, output encoding
- **Sensitive data**: Hardcoded secrets, insecure storage

#### Performance Checks

- **Algorithmic complexity**: O(n²) loops, unnecessary iterations
- **Resource usage**: Memory leaks, file handle leaks
- **Database queries**: N+1 queries, missing indexes
- **Caching opportunities**: Repeated expensive operations

### Step 3: Generate Report

Structure the review as:

```markdown
# Code Review Report

## Summary
- Overall quality score: X/10
- Critical issues: N
- Warnings: M
- Suggestions: K

## Critical Issues
### Issue 1: [Title]
- **Location**: file.py:line
- **Severity**: Critical
- **Description**: ...
- **Fix**: ...

## Warnings
...

## Suggestions
...

## Best Practices
...

## Positive Findings
...
```

## Review Templates

### Python

```python
# Check for:
- PEP 8 compliance
- Type hints
- Docstrings
- Error handling
- Resource management (with statements)
- List comprehensions vs generators
- f-strings vs format()
- Proper imports (absolute vs relative)
```

### JavaScript/TypeScript

```javascript
// Check for:
- ESLint rules
- TypeScript strict mode
- Error handling (try/catch, promises)
- Async/await vs .then()
- Arrow functions
- Destructuring
- Optional chaining
- Nullish coalescing
```

## Severity Levels

- **Critical**: Security vulnerabilities, data loss risks, crashes
- **Warning**: Performance issues, maintainability problems
- **Suggestion**: Style improvements, optimization opportunities
- **Info**: Positive findings, good practices observed

## Example Review

### Input

```python
def process_data(data):
    result = []
    for item in data:
        if item['status'] == 'active':
            result.append(item['value'] * 2)
    return result
```

### Output

```markdown
### Warning: Potential KeyError
- **Location**: process_data.py:4
- **Severity**: Warning
- **Description**: Accessing 'status' key without checking existence
- **Fix**: Use `.get()` method with default value

```python
if item.get('status') == 'active':
    result.append(item.get('value', 0) * 2)
```

### Suggestion: Use List Comprehension
- **Location**: process_data.py:3-5
- **Severity**: Suggestion
- **Description**: Loop can be simplified with list comprehension
- **Fix**:

```python
def process_data(data):
    return [item.get('value', 0) * 2 
            for item in data 
            if item.get('status') == 'active']
```
```

## Tools Integration

- Use `grep` to search for patterns
- Use `glob` to find files by pattern
- Use `read` to examine file contents
- Reference language-specific style guides

## Notes

- Be constructive, not critical
- Explain the "why" behind suggestions
- Prioritize issues by impact
- Acknowledge good practices
- Provide actionable fixes, not just problems