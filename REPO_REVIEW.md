# Repository Review: EcommerceTools

**Review Date:** 2025-11-13
**Reviewer:** Claude
**Repository:** https://github.com/practical-data-science/ecommercetools
**Current Version:** 0.42.8 (setup.py) / 0.38 (__init__.py - MISMATCH!)
**Lines of Code:** ~3,714 Python LOC

---

## Executive Summary

EcommerceTools is a Python data science toolkit for ecommerce, marketing science, and technical SEO. While the package provides useful functionality with good modular organization, it suffers from **critical technical debt** that prevents it from working with modern dependencies and represents poor library design practices.

### Overall Rating: ⚠️ **Needs Significant Work**

**Critical Issues:**
- ❌ **BREAKING:** Uses deprecated pandas methods (won't work with pandas 2.x)
- ❌ **BREAKING:** Incorrect dependency specification (`sklearn` instead of `scikit-learn`)
- ❌ **CRITICAL:** Library calls `exit()` and `sys.exit()` (violates library best practices)
- ❌ **HIGH:** Massive code duplication across modules
- ❌ **HIGH:** No rate limiting on web scraping (will get IP banned)
- ❌ **MEDIUM:** Version mismatch between setup.py (0.42.8) and __init__.py (0.38)

**Strengths:**
- ✅ Good modular organization by domain
- ✅ Comprehensive feature set for ecommerce analytics
- ✅ MIT licensed
- ✅ Well-documented README with examples
- ✅ No hardcoded credentials or obvious security vulnerabilities

---

## 1. Project Structure

### Organization: ✅ Good

```
ecommercetools/
├── advertising/      # Ad keyword generation, spintax
├── customers/        # RFM, cohorts, CLV prediction
├── marketing/        # Trading calendar
├── nlp/             # Text summarization
├── operations/      # ABC inventory classification
├── products/        # Product analytics, repurchase rates
├── reports/         # Reporting functions
├── seo/             # SEO tools (8 modules)
├── transactions/    # Transaction processing
└── utilities/       # Data loading helpers
```

**Strengths:**
- Clear separation of concerns
- Logical domain-based organization
- Each module has its own subdirectory

**Issues:**
- No `tests/` directory - **no test suite exists**
- No `docs/` directory - only README
- Missing `CONTRIBUTING.md`, `CHANGELOG.md`

---

## 2. Critical Issues

### 2.1 Deprecated Pandas Methods ❌ BREAKING

**Severity:** CRITICAL
**Impact:** Package will not work with pandas 2.0+

The codebase extensively uses `DataFrame.append()`, which was **deprecated in pandas 1.4.0** and **removed in pandas 2.0.0**.

**Affected Files:**
- `ecommercetools/customers/customers.py:211`
- `ecommercetools/seo/sitemaps.py:120`
- `ecommercetools/seo/scraping.py:181`
- `ecommercetools/seo/google_pagespeed_insights.py:117,123,130`

**Example (Current - BROKEN):**
```python
df = df.append(row, ignore_index=True)
```

**Should be:**
```python
df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
```

**Fix Priority:** IMMEDIATE

---

### 2.2 Library Calls exit() ❌ CRITICAL

**Severity:** CRITICAL
**Impact:** Makes package unusable as a library

Libraries should **NEVER** call `exit()` or `sys.exit()` - they should raise exceptions instead.

**Affected Files:**
- `ecommercetools/seo/google_search.py:26-36` (multiple `exit()` calls)
- `ecommercetools/seo/google_pagespeed_insights.py:34-36` (`sys.exit(1)`)
- `ecommercetools/seo/google_search_console.py:30` (`sys.exit(1)`)

**Example (google_search.py:26-36):**
```python
elif response.status_code == 429:
    print('Error: Too many requests...')
    exit()  # ❌ WRONG - kills the entire Python process!
```

**Should be:**
```python
elif response.status_code == 429:
    raise RuntimeError('Error: Too many requests. Rate limit exceeded.')
```

**Impact:** If a user's script calls a function that triggers this, their **entire application terminates** - unacceptable for a library.

**Fix Priority:** IMMEDIATE

---

### 2.3 Incorrect Dependencies ❌ BREAKING

**Severity:** CRITICAL
**Impact:** Installation fails

**File:** `requirements.txt:4`
```python
sklearn~=0.0  # ❌ WRONG package name
```

**Should be:**
```python
scikit-learn~=0.24.1
```

**Issue:** `sklearn` is a deprecated/dummy package on PyPI. The actual package is `scikit-learn`.

**Also:** The `import` statement uses:
```python
from sklearn.cluster import KMeans  # This works because scikit-learn provides 'sklearn'
```

But the package name in pip is `scikit-learn`.

**Fix Priority:** IMMEDIATE

---

### 2.4 Version Mismatch ❌ HIGH

**Severity:** HIGH
**Impact:** Confusion, incorrect version reporting

```python
# setup.py:12
version='0.42.8'

# ecommercetools/__init__.py:1
__version__ = "0.38"
```

**Issue:** Package version is inconsistent. Users checking `ecommercetools.__version__` will see 0.38, but pip shows 0.42.8.

**Fix Priority:** HIGH - Update __init__.py to match setup.py

---

### 2.5 Massive Code Duplication ❌ HIGH

**Severity:** HIGH
**Impact:** Maintenance nightmare, bug propagation

The `_get_source()` helper function is **duplicated across 5 files**:

1. `seo/google_autocomplete.py:12-28`
2. `seo/google_search.py:13-37`
3. `seo/google_knowledge_graph.py:8-25`
4. `seo/robots.py:12-28`
5. `seo/scraping.py:11-28`

**Impact:** Bug fixes must be applied 5 times. Different versions may drift over time.

**ABC classification logic duplicated:**
- `customers/customers.py:159-174` - `_abc_classify_customer()`
- `operations/operations.py:5-20` - `_abc_classify_product()`

**Fix:** Create `ecommercetools/utilities/http.py` with shared `get_source()` function.

**Fix Priority:** HIGH

---

## 3. Web Scraping & API Issues

### 3.1 No Rate Limiting ❌ HIGH

**Severity:** HIGH
**Impact:** IP bans, API quota exhaustion

**All SEO scraping modules lack rate limiting:**
- `google_search.py` - Pagination runs in tight loop (lines 229-236)
- `google_autocomplete.py` - No delays between requests
- `scraping.py` - No throttling

**Consequences:**
- Will hit Google's rate limits
- IP may get banned
- API quota exhausted rapidly

**Fix Priority:** HIGH - Add configurable delays/rate limiting

---

### 3.2 Hardcoded CSS Selectors ⚠️ HIGH

**Severity:** HIGH
**Impact:** Will break when Google updates UI

**File:** `seo/google_search.py:161-165`
```python
css_identifier_result = ".tF2Cxc"  # Google changes these frequently!
css_identifier_title = "h3"
css_identifier_link = ".yuRUbf a"
css_identifier_text = ".VwiC3b"
```

**Issue:** Google frequently changes CSS class names. This **WILL** break without warning.

**Recommendations:**
1. Document that scraping is fragile
2. Add version/date of last verification
3. Consider using official APIs where available
4. Add fallback selectors

**Fix Priority:** MEDIUM - Document limitations

---

### 3.3 No Retry Logic or Error Handling ⚠️ MEDIUM

**Issues:**
- Network failures cause immediate failure
- No exponential backoff for 429 (rate limit) responses
- No retry on transient errors (500, 502, 503)

**Fix Priority:** MEDIUM

---

## 4. Code Quality Issues

### 4.1 No Type Hints ⚠️ MEDIUM

**Severity:** MEDIUM
**Impact:** Poor IDE support, no type checking

**Entire codebase lacks type hints.** Python 3.6+ supports type hints, but none are used.

**Current:**
```python
def get_customers(transaction_items):
    """Return a Pandas DataFrame of customers...

    Args:
        transaction_items (object): DataFrame containing order_id, sku...
    """
```

**Should be:**
```python
def get_customers(transaction_items: pd.DataFrame) -> pd.DataFrame:
    """Return a Pandas DataFrame of customers..."""
```

**Benefits of type hints:**
- Better IDE autocomplete
- Catch errors before runtime with mypy
- Self-documenting code

**Fix Priority:** MEDIUM (quality improvement)

---

### 4.2 Logic Error in RFM Segmentation ⚠️ MEDIUM

**Severity:** MEDIUM
**Impact:** Incorrect customer segmentation

**File:** `customers/customers.py:106`
```python
elif (rfm == 455) or (rfm >= 542) & (rfm <= 555):
    return 'Star'
```

**Issue:** Operator precedence error. `&` binds tighter than `or`, so this evaluates as:
```python
(rfm == 455) or ((rfm >= 542) & (rfm <= 555))
```

**Should be:**
```python
elif (rfm == 455) or ((rfm >= 542) and (rfm <= 555)):
    return 'Star'
```

**Fix Priority:** MEDIUM - Verify intended logic and fix

---

### 4.3 Outdated Patterns ⚠️ LOW

**Issue:** Uses deprecated `pd.to_datetime('today')`

**Locations:**
- `customers/customers.py:33-34`
- `products/products.py:34-35`

**Should use:**
```python
pd.Timestamp.now()  # or datetime.now()
```

**Fix Priority:** LOW (works but deprecated)

---

## 5. Dependency Management

### Current State: ⚠️ Problematic

**requirements.txt:**
```
requests~=2.26.0        # From 2021 - outdated
pandas~=1.2.4           # From 2021 - won't work with code (needs <2.0)
sklearn~=0.0            # ❌ WRONG package name
transformers~=4.5.1     # From 2021 - very outdated
torch                   # No version pinning - dangerous
```

**Issues:**
1. **Outdated versions** - All from 2021
2. **Conflicting requirements** - Code requires pandas <2.0 but doesn't specify
3. **Missing version pins** - `torch` unpinned (could pull 2GB+ package)
4. **Wrong package name** - `sklearn` should be `scikit-learn`

**Recommendations:**
1. Update to modern versions (2024/2025)
2. Fix deprecated pandas usage first
3. Add upper bound for pandas: `pandas>=1.4.0,<2.0.0` (until code is fixed)
4. Consider making heavy deps (torch, transformers) optional

---

## 6. Testing

### Current State: ❌ CRITICAL

**No test suite exists.**

Only file: `ecommercetools/seo/testing.py` - Not a test file, appears to be test/demo code.

**Implications:**
- No confidence changes don't break existing functionality
- Can't refactor safely
- Can't verify compatibility with new pandas versions

**Recommendations:**
1. Add `pytest` as dev dependency
2. Create `tests/` directory
3. Write unit tests for core functions
4. Add integration tests for API functions (with mocking)
5. Set up CI to run tests on PRs

**Priority:** HIGH

---

## 7. CI/CD

### Current State: ⚠️ Problematic

**File:** `.github/workflows/python-publish.yml`

**Issues:**

1. **Publishes on EVERY push** (line 6):
```yaml
on: [push]  # ❌ Will publish to PyPI on every commit!
```

**Should be:**
```yaml
on:
  release:
    types: [published]
```

2. **No testing before publishing**
   - No tests run
   - No linting
   - No type checking

3. **No checks on PRs**
   - No CI for pull requests
   - No code quality gates

**Recommendations:**
1. Only publish on tagged releases
2. Add test job before deployment
3. Add linting (ruff/flake8)
4. Add type checking (mypy)
5. Add PR checks

**Priority:** HIGH (currently publishing on every push is dangerous)

---

## 8. Security Assessment

### Overall: ✅ Good (No Critical Issues Found)

**Positives:**
- ✅ No hardcoded credentials
- ✅ API keys passed as parameters
- ✅ No SQL injection risks (uses pandas/ORM)
- ✅ No eval() or exec() usage

**Minor Concerns:**
- ⚠️ No input validation on file paths (could load arbitrary files)
- ⚠️ No URL validation before HTTP requests
- ⚠️ `.gitignore` includes credential files (good) but examples reference them

**Recommendations:**
- Add path validation for file operations
- Add URL validation/sanitization
- Consider using `pathlib.Path` for path operations

---

## 9. Documentation

### README: ✅ Excellent

**Strengths:**
- Comprehensive examples for all features
- Clear installation instructions
- Well-organized by module
- Good use of tables and code examples

**Areas for improvement:**
- No API reference docs
- No developer/contributor guide
- No changelog
- Examples in README may be out of date (uses deprecated patterns)

### Code Documentation: ✅ Good

**Strengths:**
- Most functions have docstrings
- Consistent Args/Returns format

**Weaknesses:**
- No module-level docstrings
- Some parameter descriptions vague ("Pandas DataFrame")
- Missing examples in complex functions
- Inconsistent parameter names (e.g., "df" vs actual parameter name)

**Example issue (reports/reports.py:54-58):**
```python
def customers_report(transaction_items_df, frequency='M'):
    """...
    Args:
        df (dataframe): ...  # ❌ Wrong parameter name!
```

---

## 10. Package Metadata

### setup.py Analysis

**Good:**
- ✅ Long description from README
- ✅ Good keywords
- ✅ Clear author info

**Issues:**
- ⚠️ `Programming Language :: Python :: 3.6` - Python 3.6 EOL since Dec 2021
- ⚠️ Development Status :: 3 - Alpha - Should be Beta after 42 versions?
- ⚠️ Uses legacy setuptools (should migrate to pyproject.toml)
- ❌ Wrong dependency names

**Recommendations:**
1. Update to Python 3.8+ minimum
2. Consider Beta status
3. Migrate to `pyproject.toml` (PEP 517/518)
4. Use modern build system (setuptools with pyproject.toml or hatchling)

---

## 11. Specific Module Reviews

### 11.1 Customers Module: ✅ Good

**File:** `customers/customers.py`

**Strengths:**
- Comprehensive RFM analysis
- CLV prediction using lifetimes library
- Cohort analysis
- Well-structured

**Issues:**
- Logic error in RFM segmentation (line 106)
- Uses deprecated pandas patterns
- K-means clustering hardcoded to 5 clusters (no configurability)

---

### 11.2 SEO Module: ⚠️ High Risk

**Multiple submodules** (8 files)

**Critical Issues:**
- Massive code duplication
- Hardcoded CSS selectors (will break)
- No rate limiting (will get banned)
- Calls exit() on errors
- No retry logic

**This module needs the most work.**

---

### 11.3 NLP Module: ⚠️ Concerning

**File:** `nlp/nlp.py`

**Issues:**
- Pulls 1.2GB+ transformers model with no warning
- No model caching configuration shown
- No model versioning
- Could fail with newer transformers versions

**Recommendations:**
- Document model size and requirements
- Allow model selection
- Add progress indicators
- Consider making this an optional dependency

---

## 12. Recommendations Summary

### Immediate (Before Next Release)

1. **Fix pandas compatibility**
   - Replace all `df.append()` with `pd.concat()`
   - Add pandas version constraint: `pandas>=1.4.0,<2.0.0`

2. **Fix dependencies**
   - Change `sklearn~=0.0` to `scikit-learn~=0.24.1`

3. **Fix version mismatch**
   - Update `__init__.py` to version 0.42.8

4. **Fix CI/CD**
   - Change publish trigger from `[push]` to release events

5. **Remove exit() calls**
   - Replace with proper exception raising

### High Priority (Next Sprint)

6. **Consolidate duplicate code**
   - Create shared `utilities/http.py` module
   - Refactor `_get_source()` usage

7. **Add testing infrastructure**
   - Set up pytest
   - Write tests for core functions
   - Add CI test runs

8. **Add rate limiting**
   - Implement throttling in SEO modules
   - Add configurable delays

### Medium Priority

9. **Add type hints**
   - Gradually add to new/modified functions
   - Run mypy

10. **Improve error handling**
    - Replace broad `except Exception`
    - Add specific exception types
    - Add retry logic

11. **Fix logic errors**
    - RFM segmentation operator precedence

### Low Priority

12. **Modernize**
    - Migrate to pyproject.toml
    - Update to Python 3.8+ minimum
    - Update dependencies to 2024/2025 versions

13. **Documentation**
    - Add CHANGELOG.md
    - Add CONTRIBUTING.md
    - Generate API docs (Sphinx)

---

## 13. Scoring

| Category | Score | Notes |
|----------|-------|-------|
| **Code Quality** | 5/10 | Clean but outdated patterns |
| **Testing** | 0/10 | No tests |
| **Documentation** | 7/10 | Good README, decent docstrings |
| **Dependencies** | 3/10 | Outdated, incorrect specs |
| **Security** | 8/10 | No major issues |
| **Maintainability** | 4/10 | High duplication, no tests |
| **API Design** | 6/10 | Good structure, poor error handling |
| **CI/CD** | 3/10 | Publishes on every push, no tests |
| **Compatibility** | 2/10 | Won't work with modern pandas |
| **Overall** | **4.2/10** | **Needs significant work** |

---

## 14. Conclusion

EcommerceTools provides valuable functionality for ecommerce analytics, but **critical technical debt prevents production use**. The package:

- ❌ **Cannot work with pandas 2.x** (deprecated methods)
- ❌ **Cannot install properly** (wrong dependency names)
- ❌ **Will terminate user applications** (calls exit())
- ❌ **Will get banned by Google** (no rate limiting)
- ❌ **Has no tests** (cannot safely refactor)

### Verdict

**Not recommended for production use** until critical issues are resolved.

### Path Forward

1. Fix breaking issues (pandas, dependencies, exit calls)
2. Add test suite
3. Fix CI/CD to only publish on releases
4. Address code duplication
5. Add rate limiting
6. Consider pandas 2.x migration

With these fixes, this could be a solid library. The functionality is there, but the implementation needs modernization.

---

## Positive Notes

Despite the issues, the project has several strengths:

- ✅ Solves real problems in ecommerce analytics
- ✅ Well-organized module structure
- ✅ Comprehensive feature set
- ✅ Good documentation for users
- ✅ Active development (42 versions published)
- ✅ Open source with permissive license

**The foundation is good - it just needs technical debt cleanup.**
