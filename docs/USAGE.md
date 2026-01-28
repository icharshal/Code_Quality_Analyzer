# 📖 Usage Guide - Code Quality Analyzer

This guide explains how to use the Code Quality Analyzer to analyze your Python code.

---

## 🚀 Quick Start

### **Step 1: Prepare Your Code**

Place your Python file in a location accessible to the analyzer.

---

### **Step 2: Run Analysis**

```python
python analyzer.py --file your_script.py --output report.md
```

---

### **Step 3: Review Report**

Open the generated `report.md` file to see the analysis results.

---

## 🔍 Analysis Categories

### **1. Code Structure (Weight: 20%)**

Analyzes:

- Class organization
- Method length and complexity
- Single Responsibility Principle
- Modularity
- Code duplication

**Example Issues**:

- ❌ Method too long (>100 lines)
- ❌ Class doing too many things
- ✅ Well-organized, modular code

---

### **2. Error Handling (Weight: 20%)**

Analyzes:

- Exception handling completeness
- Bare except clauses
- Resource cleanup (try/finally)
- Retry logic
- Error logging

**Example Issues**:

- ❌ Bare `except:` clause
- ❌ Missing resource cleanup
- ✅ Comprehensive error handling with retries

---

### **3. Performance (Weight: 15%)**

Analyzes:

- Threading/concurrency usage
- Memory efficiency
- API call optimization
- Caching strategies
- Algorithm complexity

**Example Issues**:

- ❌ Inefficient loops
- ❌ No caching for repeated calls
- ✅ Multi-threaded processing with batch optimization

---

### **4. Security (Weight: 15%)**

Analyzes:

- Authentication methods
- Secret management
- Input validation
- SQL injection risks
- Path traversal vulnerabilities

**Example Issues**:

- ❌ Hardcoded credentials
- ❌ No input sanitization
- ✅ Service account authentication with proper scopes

---

### **5. Maintainability (Weight: 15%)**

Analyzes:

- Code readability
- Naming conventions
- Documentation (docstrings)
- Type hints
- Comments

**Example Issues**:

- ❌ Missing docstrings
- ❌ No type hints
- ✅ Clear naming, comprehensive documentation

---

### **6. Best Practices (Weight: 15%)**

Analyzes:

- PEP 8 compliance
- Python idioms
- Design patterns
- Testing
- Logging

**Example Issues**:

- ❌ Not following PEP 8
- ❌ No unit tests
- ✅ Follows Python best practices

---

## 📊 Understanding Scores

### **Overall Quality Score**

| Score | Rating | Meaning |
|-------|--------|---------|
| 9.0-10.0 | ⭐⭐⭐⭐⭐ Excellent | Production ready, minimal improvements needed |
| 7.0-8.9 | ⭐⭐⭐⭐☆ Good | Minor improvements recommended |
| 5.0-6.9 | ⭐⭐⭐☆☆ Fair | Significant improvements needed |
| 3.0-4.9 | ⭐⭐☆☆☆ Poor | Major refactoring required |
| 0.0-2.9 | ⭐☆☆☆☆ Critical | Not production ready |

---

### **Bug Severity Levels**

| Severity | Priority | Action Required |
|----------|----------|-----------------|
| 🔴 **Critical** | Immediate | Prevents execution, fix now |
| 🟠 **High** | Urgent | Causes failures, fix before deployment |
| 🟡 **Medium** | Important | May cause issues, fix soon |
| 🟢 **Low** | Optional | Minor issues, fix when convenient |

---

## 📝 Report Sections

### **1. Executive Summary**

Quick overview with:

- Overall quality score
- Category scores
- Production readiness verdict
- Critical issues count

---

### **2. Detailed Analysis**

In-depth review including:

- Specific issues with line numbers
- Code examples
- Recommended fixes
- Impact assessment

---

### **3. Metrics**

Quantitative measurements:

- Lines of code
- Cyclomatic complexity
- Code duplication percentage
- Test coverage
- Documentation coverage

---

### **4. Recommendations**

Prioritized list of improvements:

- Critical fixes (must do)
- High priority (should do)
- Medium priority (nice to have)
- Low priority (optional)

---

## 🎯 Example Analysis

### **Input Code**

```python
def process_data(data):
    try:
        result = []
        for item in data:
            result.append(item * 2)
        return result
    except:
        print("Error")
        return None
```

### **Analysis Output**

**Issues Found**:

1. 🟠 **High**: Bare except clause (line 7)
   - **Problem**: Catches all exceptions, including system exits
   - **Fix**: Use specific exception types

   ```python
   except (ValueError, TypeError) as e:
       logger.error(f"Error processing data: {e}")
   ```

2. 🟡 **Medium**: No type hints (line 1)
   - **Problem**: Reduces IDE support and clarity
   - **Fix**: Add type hints

   ```python
   def process_data(data: List[int]) -> Optional[List[int]]:
   ```

3. 🟢 **Low**: List comprehension could be used (line 4-5)
   - **Problem**: Less Pythonic
   - **Fix**: Use list comprehension

   ```python
   result = [item * 2 for item in data]
   ```

**Score**: 6.5/10 (Fair)

---

## 🔧 Advanced Usage

### **Custom Analysis Rules**

Create a `config.yaml` file:

```yaml
rules:
  max_method_length: 100
  max_complexity: 10
  require_type_hints: true
  require_docstrings: true
  
severity:
  bare_except: high
  missing_docstring: medium
  long_method: low
```

Run with config:

```bash
python analyzer.py --file script.py --config config.yaml
```

---

### **Batch Analysis**

Analyze multiple files:

```bash
python analyzer.py --directory ./src --output reports/
```

---

### **CI/CD Integration**

Add to your pipeline:

```yaml
# .github/workflows/quality.yml
- name: Code Quality Check
  run: |
    python analyzer.py --file src/main.py --fail-on-score 7.0
```

---

## 📈 Improving Your Score

### **Quick Wins**

1. **Add Type Hints** (+0.5 points)

   ```python
   def process(data: str) -> int:
   ```

2. **Add Docstrings** (+0.5 points)

   ```python
   """Process the input data and return result."""
   ```

3. **Fix Bare Excepts** (+1.0 point)

   ```python
   except ValueError as e:
   ```

4. **Add Logging** (+0.3 points)

   ```python
   logger.error(f"Failed: {e}")
   ```

---

### **Major Improvements**

1. **Add Error Handling** (+1.5 points)
   - Comprehensive try/except blocks
   - Retry logic
   - Resource cleanup

2. **Optimize Performance** (+1.0 point)
   - Use threading/async
   - Add caching
   - Batch operations

3. **Improve Security** (+1.0 point)
   - Remove hardcoded secrets
   - Add input validation
   - Use proper authentication

---

## 🐛 Troubleshooting

### **Issue: Analyzer not finding issues**

**Cause**: Code might already be high quality

**Solution**: Check the report for positive feedback

---

### **Issue: Too many false positives**

**Cause**: Overly strict rules

**Solution**: Adjust config file or ignore specific warnings

---

### **Issue: Score seems too low**

**Cause**: Multiple categories affected

**Solution**: Focus on high-impact fixes first (error handling, security)

---

## 📚 Best Practices

1. **Run regularly**: Analyze code before every commit
2. **Set standards**: Define minimum acceptable score for your team
3. **Track progress**: Keep historical reports to see improvements
4. **Focus on critical**: Fix critical and high priority issues first
5. **Learn from reports**: Use as a learning tool for best practices

---

## 🎓 Learning Resources

- **PEP 8**: Python style guide
- **PEP 484**: Type hints
- **Clean Code**: Robert C. Martin
- **Effective Python**: Brett Slatkin

---

## 📞 Support

For questions or issues:

1. Check the [FAQ](docs/FAQ.md)
2. Review [example reports](examples/)
3. Open an issue on GitHub

---

**Analyze. Learn. Improve.** 🚀
