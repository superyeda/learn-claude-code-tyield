---
name: code-review
description: Perform thorough code reviews with security, performance, and style analysis
---

# Code Review Skill

When asked to review code, follow this structured review process. Produce a clear, actionable report.

## Review Process

### Step 1: Understand Context

Before reviewing, gather context:
- What language/framework is this?
- What is the purpose of this code?
- Are there related files (tests, configs, types)?

Use `read_file` and `glob` to explore the codebase.

### Step 2: Multi-Dimensional Analysis

Evaluate the code across these dimensions:

#### 1. Correctness
- Logic errors, off-by-one bugs
- Null/undefined handling
- Edge cases not covered
- Race conditions (async code)
- Error handling gaps

#### 2. Security
- Input validation missing?
- SQL injection / command injection / XSS
- Hardcoded secrets or credentials
- Path traversal vulnerabilities
- Unsafe deserialization

#### 3. Performance
- N+1 queries or unnecessary loops
- Missing caching opportunities
- Memory leaks or unbounded growth
- Blocking calls in async context
- Large data loaded into memory

#### 4. Readability
- Naming: variables, functions, classes
- Function length (flag > 50 lines)
- Comment quality (why, not what)
- Consistent formatting
- Magic numbers → named constants

#### 5. Maintainability
- DRY violations (duplicated logic)
- Single Responsibility Principle
- Coupling between modules
- Test coverage gaps
- Missing type hints / documentation

### Step 3: Generate Report

Format your review as:

```markdown
## Code Review Summary

**Files reviewed**: N files
**Overall rating**: ⭐⭐⭐⭐ (4/5)

### 🔴 Critical Issues (must fix)
1. **[file:line]** — Description of issue
   ```language
   // problematic code
   ```
   **Fix**: Suggested fix

### 🟡 Warnings (should fix)
1. ...

### 🟢 Suggestions (nice to have)
1. ...

### ✅ What's done well
1. ...
```

## Severity Levels

| Level | Icon | Meaning |
|-------|------|---------|
| Critical | 🔴 | Bugs, security holes, data loss risk |
| Warning | 🟡 | Performance, anti-patterns, tech debt |
| Suggestion | 🟢 | Style, readability, best practices |
| Positive | ✅ | Good patterns worth highlighting |

## Language-Specific Checklists

### Python
- [ ] Type hints present?
- [ ] f-strings vs .format() consistency?
- [ ] Context managers for resources?
- [ ] `if __name__ == "__main__"` guard?
- [ ] Exception specificity (not bare `except`)?

### JavaScript/TypeScript
- [ ] `===` vs `==`?
- [ ] Async/await error handling?
- [ ] Nullish coalescing (`??`) vs `||`?
- [ ] Proper TypeScript types (no `any`)?
- [ ] Memory leak in useEffect cleanup?

### Go
- [ ] Error values checked?
- [ ] Goroutine leaks?
- [ ] Context propagation?
- [ ] Defer in loops?
- [ ] Interface satisfaction?

## Review Rules

1. **Be specific**: Always include file path and line number
2. **Show the fix**: Don't just point out problems, suggest solutions
3. **Prioritize**: Critical issues first
4. **Be constructive**: Highlight what's done well too
5. **Stay focused**: Review the code, not the author
