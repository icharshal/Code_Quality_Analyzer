# 🔍 Code Quality Analyzer

A comprehensive Python code quality analysis tool that automatically analyzes your code and generates detailed quality reports.

---

## 📋 Overview

This tool analyzes Python code files and generates detailed quality reports including:

- ✅ **Bug Detection** - Critical, high, medium, and low priority issues
- ✅ **Code Structure** - Function length, complexity, duplication
- ✅ **Error Handling** - Try/except coverage, bare except clauses
- ✅ **Performance** - Inefficient patterns, optimization opportunities
- ✅ **Security** - Hardcoded secrets, dangerous functions
- ✅ **Maintainability** - Docstrings, type hints, naming conventions
- ✅ **Best Practices** - PEP 8 compliance, Python idioms

---

## 🚀 Quick Start

### **Installation**

```bash
# Clone the repository
git clone https://github.com/icharshal/Code_Quality_Analyzer.git
cd Code_Quality_Analyzer

# No dependencies required - uses Python standard library only!
```

### **Usage**

```bash
# Analyze a single file
python analyzer.py --file your_script.py

# Analyze all Python files in a directory
python analyzer.py --directory ./src

# Save report to file (coming soon)
python analyzer.py --file script.py --output report.md
```

---

## 📊 Example Output

```
================================================================================
📊 CODE QUALITY REPORT - sample_code.py
================================================================================

🎯 Overall Quality Score: 6.2/10 ⭐⭐⭐☆☆

📈 Category Scores:
  - Structure: 9.5/10
  - Error Handling: 8.0/10
  - Performance: 9.7/10
  - Security: 7.0/10
  - Maintainability: 8.0/10
  - Best Practices: 9.6/10

📏 Code Metrics:
  - Lines of Code: 20
  - Functions: 3
  - Classes: 1
  - Avg Function Length: 4.3 lines

🐛 Issues Found: 4

  CRITICAL (1):
    - Line 15: Hardcoded Secret
      Potential hardcoded secret found

  HIGH (1):
    - Line 11: Bare Except Clause
      Using bare except: catches all exceptions including system exits

  LOW (2):
    - Line 12: Print Statement
      Consider using logging instead of print()
    - Line 18: Naming Convention
      Function 'VeryLongFunctionName' should use snake_case

================================================================================
⚠️  NEEDS IMPROVEMENT - Significant refactoring recommended
================================================================================
```

---

## 📁 Repository Contents

```
Code_Quality_Analyzer/
├── README.md                          # This file
├── analyzer.py                        # Main analyzer tool ⭐
├── reports/
│   ├── CODE_QUALITY_REPORT_FINAL.md  # Example comprehensive report
│   └── QUALITY_SUMMARY.md            # Example executive summary
├── examples/
│   └── sample_code.py                # Sample code to test analyzer
└── docs/
    ├── USAGE.md                       # Detailed usage guide
    └── METRICS.md                     # Metrics explanation
```

---

## 🔍 What Gets Analyzed

### **1. Code Structure (20% weight)**

- Function and method length
- Cyclomatic complexity
- Code duplication
- Class organization

### **2. Error Handling (20% weight)**

- Try/except coverage
- Bare except clauses
- Resource cleanup
- Error logging

### **3. Performance (15% weight)**

- List comprehension opportunities
- Inefficient loops
- Algorithm complexity

### **4. Security (15% weight)**

- Hardcoded secrets (passwords, API keys, tokens)
- Dangerous functions (eval, exec)
- Input validation

### **5. Maintainability (15% weight)**

- Docstring coverage
- Type hints
- Naming conventions
- Code readability

### **6. Best Practices (15% weight)**

- PEP 8 compliance
- Python idioms
- Logging vs print statements
- Proper naming conventions

---

## 📊 Quality Scores

| Score | Rating | Meaning |
|-------|--------|---------|
| 9.0-10.0 | ⭐⭐⭐⭐⭐ Excellent | Production ready |
| 7.0-8.9 | ⭐⭐⭐⭐☆ Good | Minor improvements needed |
| 5.0-6.9 | ⭐⭐⭐☆☆ Fair | Significant improvements needed |
| 3.0-4.9 | ⭐⭐☆☆☆ Poor | Major refactoring required |
| 0.0-2.9 | ⭐☆☆☆☆ Critical | Not production ready |

---

## 🎯 Features

- ✅ **Zero Dependencies** - Uses only Python standard library
- ✅ **Fast Analysis** - Analyzes files in seconds
- ✅ **Detailed Reports** - Clear, actionable feedback
- ✅ **Multiple Files** - Analyze entire directories
- ✅ **Production Ready** - Deployment recommendations
- ✅ **Easy to Use** - Simple command-line interface

---

## 📚 Documentation

- **[USAGE.md](docs/USAGE.md)** - Detailed usage guide with examples
- **[METRICS.md](docs/METRICS.md)** - Explanation of all metrics and scoring
- **[Example Reports](reports/)** - Sample analysis reports

---

## 🛠️ Use Cases

1. **Pre-Deployment Review** - Check code quality before production
2. **Code Review** - Automated analysis for pull requests
3. **Learning Tool** - Understand Python best practices
4. **Technical Debt** - Identify areas needing refactoring
5. **Team Standards** - Ensure consistent code quality

---

## 📈 Example Analysis

**Input**: `sample_code.py` (20 lines)

**Output**:

- Overall Score: 6.2/10
- Issues Found: 4 (1 critical, 1 high, 2 low)
- Recommendation: Fix critical security issue before deployment

**Time**: < 1 second

---

## 🤝 Contributing

Contributions are welcome! This tool can be extended with:

- Additional analysis rules
- Custom scoring weights
- Export formats (JSON, HTML, PDF)
- CI/CD integration
- IDE plugins

---

## 📝 License

MIT License - Feel free to use and modify

---

## 🎯 Real-World Example

This analyzer was used to analyze a production Google Drive to GCS migration script:

**Results**:

- Identified 2 critical bugs
- Found 4 high-priority issues
- Provided specific fixes for each issue
- After fixes: Score improved from 8.2/10 to 9.5/10
- Successfully deployed to production handling 12TB+ data

---

## 📞 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Analyze your code. Ship with confidence.** 🚀
