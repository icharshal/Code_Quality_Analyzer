# ❓ Frequently Asked Questions (FAQ)

## 🌐 Vercel & Deployment

### Why am I getting a `404: NOT_FOUND` error on Vercel?

This usually happens when you try to access a page directly or refresh a page on a single-page application or a static site where routing is handled on the client side.

**Solution**: Ensure you have a `vercel.json` file in your root directory with the following configuration:

```json
{
  "cleanUrls": true
}
```

This allows you to access documentation and reports without needing to include the `.md` or `.html` extension in the URL.

---

## 🐍 Python & Imports

### Why am I getting a `ModuleNotFoundError` when running tests?

If your tests are in a subfolder and they try to import modules from the same folder or a parent folder, Python might not find them depending on how you run the tests.

**Solution**: You can programmatically add the directory containing the module to `sys.path` in your test file:

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
```

Alternatively, run tests from the project root using:
```bash
python3 -m unittest discover examples/
```

---

## 📊 Analyzer Usage

### How do I improve my code quality score?

- **Add Type Hints**: Use `typing` to annotate function arguments and return types.
- **Add Docstrings**: Use triple quotes `"""` to document your functions and classes.
- **Handle Specific Exceptions**: Avoid bare `except:` clauses; catch specific errors like `ValueError`.
- **Use Logging**: Replace `print()` statements with the `logging` module.

### Why is the analyzer flagging my "hardcoded secret" which is just a test string?

The analyzer uses regex to find potential secrets. If it flags a non-sensitive string, you can either rename the variable or move it to a configuration file that is ignored by the analyzer.
