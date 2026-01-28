# 📊 Metrics Guide - Code Quality Analyzer

This guide explains all the metrics used in the code quality analysis.

---

## 🎯 Overall Quality Score

**Formula**: Weighted average of all category scores

```
Overall Score = (Structure × 0.20) + (Error Handling × 0.20) + 
                (Performance × 0.15) + (Security × 0.15) + 
                (Maintainability × 0.15) + (Best Practices × 0.15)
```

**Range**: 0.0 - 10.0

**Interpretation**:

- **9.0-10.0**: Excellent - Production ready
- **7.0-8.9**: Good - Minor improvements
- **5.0-6.9**: Fair - Significant work needed
- **3.0-4.9**: Poor - Major refactoring required
- **0.0-2.9**: Critical - Not production ready

---

## 📐 Category Metrics

### **1. Code Structure (20% weight)**

#### **Metrics Measured**

| Metric | Description | Good | Bad |
|--------|-------------|------|-----|
| **Method Length** | Lines per method | <50 | >100 |
| **Class Cohesion** | Related methods grouped | High | Low |
| **Cyclomatic Complexity** | Decision points | <10 | >20 |
| **Code Duplication** | Repeated code | <5% | >15% |
| **Modularity** | Single responsibility | Yes | No |

#### **Calculation**

```
Structure Score = (Method Length Score + Cohesion Score + 
                  Complexity Score + Duplication Score + 
                  Modularity Score) / 5
```

#### **Example**

```python
# Good (9/10)
class FileProcessor:
    def process(self, file):
        data = self.read(file)
        return self.transform(data)
    
    def read(self, file):
        # 10 lines
        
    def transform(self, data):
        # 15 lines

# Bad (4/10)
class FileProcessor:
    def process_everything(self, file):
        # 200 lines of mixed responsibilities
```

---

### **2. Error Handling (20% weight)**

#### **Metrics Measured**

| Metric | Description | Good | Bad |
|--------|-------------|------|-----|
| **Exception Coverage** | % of risky code in try/except | >90% | <50% |
| **Specific Exceptions** | Using specific vs bare except | Specific | Bare |
| **Resource Cleanup** | finally blocks or context managers | Yes | No |
| **Retry Logic** | Handling transient failures | Yes | No |
| **Error Logging** | Logging exceptions | Yes | No |

#### **Calculation**

```
Error Handling Score = (Coverage × 0.3) + (Specificity × 0.3) + 
                       (Cleanup × 0.2) + (Retry × 0.1) + 
                       (Logging × 0.1)
```

#### **Example**

```python
# Good (9/10)
def process_file(path):
    try:
        with open(path) as f:  # Auto cleanup
            return f.read()
    except FileNotFoundError as e:  # Specific
        logger.error(f"File not found: {e}")  # Logging
        raise
    except IOError as e:
        logger.error(f"IO error: {e}")
        raise

# Bad (3/10)
def process_file(path):
    try:
        f = open(path)  # No cleanup
        return f.read()
    except:  # Bare except
        print("Error")  # No logging
        return None
```

---

### **3. Performance (15% weight)**

#### **Metrics Measured**

| Metric | Description | Good | Bad |
|--------|-------------|------|-----|
| **Concurrency** | Using threads/async | Yes | No |
| **Memory Efficiency** | Streaming vs loading all | Stream | Load all |
| **API Optimization** | Batching, caching | Yes | No |
| **Algorithm Complexity** | O(n) vs O(n²) | O(n) | O(n²) |
| **Resource Usage** | Efficient use of resources | Yes | No |

#### **Calculation**

```
Performance Score = (Concurrency × 0.25) + (Memory × 0.25) + 
                    (API × 0.25) + (Algorithm × 0.15) + 
                    (Resources × 0.10)
```

#### **Example**

```python
# Good (9/10)
from concurrent.futures import ThreadPoolExecutor

def process_files(files):
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Concurrent processing
        results = executor.map(process_file, files)
    return list(results)

# Bad (4/10)
def process_files(files):
    results = []
    for file in files:  # Sequential
        results.append(process_file(file))
    return results
```

---

### **4. Security (15% weight)**

#### **Metrics Measured**

| Metric | Description | Good | Bad |
|--------|-------------|------|-----|
| **Authentication** | Secure auth methods | Service account | Hardcoded |
| **Secret Management** | How secrets are stored | Env vars/vault | In code |
| **Input Validation** | Sanitizing inputs | Yes | No |
| **SQL Injection** | Parameterized queries | Yes | String concat |
| **Path Traversal** | Path sanitization | Yes | No |

#### **Calculation**

```
Security Score = (Auth × 0.30) + (Secrets × 0.30) + 
                 (Validation × 0.20) + (SQL × 0.10) + 
                 (Path × 0.10)
```

#### **Example**

```python
# Good (9/10)
import os
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(
    os.environ['SERVICE_ACCOUNT_FILE']  # From env
)

# Bad (3/10)
API_KEY = "sk_live_12345..."  # Hardcoded
password = "admin123"  # Hardcoded
```

---

### **5. Maintainability (15% weight)**

#### **Metrics Measured**

| Metric | Description | Good | Bad |
|--------|-------------|------|-----|
| **Documentation** | Docstrings present | >90% | <30% |
| **Type Hints** | Type annotations | Yes | No |
| **Naming** | Clear, descriptive names | Yes | No |
| **Comments** | Helpful inline comments | Yes | Excessive |
| **Code Readability** | Easy to understand | Yes | No |

#### **Calculation**

```
Maintainability Score = (Documentation × 0.25) + (Types × 0.25) + 
                        (Naming × 0.20) + (Comments × 0.15) + 
                        (Readability × 0.15)
```

#### **Example**

```python
# Good (9/10)
def calculate_total_price(items: List[Item], tax_rate: float) -> Decimal:
    """
    Calculate total price including tax.
    
    Args:
        items: List of items to price
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
    
    Returns:
        Total price with tax applied
    """
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)

# Bad (3/10)
def calc(i, t):  # No docs, no types, bad names
    s = 0
    for x in i:
        s += x.p
    return s * (1 + t)
```

---

### **6. Best Practices (15% weight)**

#### **Metrics Measured**

| Metric | Description | Good | Bad |
|--------|-------------|------|-----|
| **PEP 8 Compliance** | Following style guide | Yes | No |
| **Python Idioms** | Pythonic code | Yes | No |
| **Design Patterns** | Appropriate patterns | Yes | No |
| **Testing** | Unit tests present | Yes | No |
| **Logging** | Proper logging | Yes | print() |

#### **Calculation**

```
Best Practices Score = (PEP8 × 0.20) + (Idioms × 0.20) + 
                       (Patterns × 0.20) + (Testing × 0.20) + 
                       (Logging × 0.20)
```

#### **Example**

```python
# Good (9/10)
import logging

logger = logging.getLogger(__name__)

def process_items(items: List[str]) -> List[str]:
    """Process items using list comprehension."""
    return [item.upper() for item in items if item]

# Bad (4/10)
def process_items(items):
    result = []
    for item in items:
        if item != "":
            result.append(item.upper())
    print("Processed")  # Using print instead of logging
    return result
```

---

## 📏 Additional Metrics

### **Lines of Code (LOC)**

**Measurement**: Total lines excluding comments and blanks

**Interpretation**:

- <500: Small, manageable
- 500-2000: Medium, well-structured needed
- >2000: Large, requires excellent organization

---

### **Cyclomatic Complexity**

**Measurement**: Number of independent paths through code

**Formula**: `E - N + 2P`

- E = edges in control flow graph
- N = nodes
- P = connected components

**Interpretation**:

- 1-10: Simple, easy to test
- 11-20: Moderate, needs attention
- 21-50: Complex, hard to maintain
- >50: Very complex, refactor needed

---

### **Code Duplication**

**Measurement**: Percentage of duplicated code blocks

**Interpretation**:

- <5%: Excellent
- 5-10%: Good
- 10-20%: Fair, consider refactoring
- >20%: Poor, significant duplication

---

### **Test Coverage**

**Measurement**: Percentage of code covered by tests

**Interpretation**:
>
- >80%: Excellent
- 60-80%: Good
- 40-60%: Fair
- <40%: Poor

---

## 🎯 Production Readiness Criteria

### **Minimum Requirements**

| Metric | Minimum | Recommended |
|--------|---------|-------------|
| Overall Score | 7.0 | 8.5 |
| Critical Bugs | 0 | 0 |
| High Priority Issues | 0 | 0 |
| Error Handling | 7.0 | 8.5 |
| Security | 7.0 | 8.5 |
| Test Coverage | 60% | 80% |

---

### **Deployment Decision Matrix**

| Overall Score | Critical Bugs | Decision |
|---------------|---------------|----------|
| ≥9.0 | 0 | ✅ Deploy immediately |
| 7.0-8.9 | 0 | ✅ Deploy with monitoring |
| 5.0-6.9 | 0 | ⚠️ Fix medium issues first |
| <5.0 | Any | ❌ Do not deploy |
| Any | >0 | ❌ Fix critical bugs first |

---

## 📈 Improvement Tracking

### **Score Improvement**

Track progress over time:

```
Improvement Rate = (New Score - Old Score) / Old Score × 100%
```

**Example**:

- Old Score: 7.5
- New Score: 8.5
- Improvement: (8.5 - 7.5) / 7.5 × 100% = 13.3%

---

### **Bug Reduction**

Track bug fixes:

```
Bug Reduction = (Old Bugs - New Bugs) / Old Bugs × 100%
```

**Example**:

- Old Bugs: 10
- New Bugs: 2
- Reduction: (10 - 2) / 10 × 100% = 80%

---

## 🔍 Interpreting Results

### **High Score, Low Bugs** (9.0+, 0 bugs)

- ✅ Excellent code quality
- ✅ Production ready
- ✅ Minimal maintenance needed

### **Medium Score, No Critical Bugs** (7.0-8.9, 0 critical)

- ✅ Good code quality
- ⚠️ Some improvements recommended
- ✅ Can deploy with monitoring

### **Low Score, Multiple Bugs** (<7.0, bugs present)

- ❌ Needs significant work
- ❌ Not production ready
- ⚠️ Focus on critical issues first

---

## 📚 References

- **PEP 8**: Python Style Guide
- **PEP 257**: Docstring Conventions
- **PEP 484**: Type Hints
- **Cyclomatic Complexity**: Thomas J. McCabe (1976)
- **Clean Code**: Robert C. Martin
- **Code Complete**: Steve McConnell

---

**Measure. Understand. Improve.** 📊
