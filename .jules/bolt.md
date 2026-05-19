## 2025-05-15 - [Consolidated AST Traversal]
**Learning:** For AST-based analyzers, calling `ast.walk()` multiple times is a significant performance bottleneck, especially for large files. Each call performs a full traversal of the tree.
**Action:** Use `ast.NodeVisitor` to collect all necessary node information in a single pass over the AST. This reduced execution time by ~64% in this codebase.

## 2025-05-16 - [Consolidated Line-Based Analysis]
**Learning:** Multiple redundant iterations over file lines for metrics, security, and duplication checks are expensive for large files.
**Action:** Implement a single `_perform_line_analysis` pass to collect all line-based data. This reduced execution time by ~29% on a 100k line file.

## 2025-05-15 - [Regex Search Optimization]
**Learning:** Searching for multiple independent regex patterns per line in a loop is expensive.
**Action:** Compile multiple patterns into a single regex object using the `|` operator and `re.compile()`. This ensures the regex engine only needs to scan each line once.

## 2025-05-15 - Optimization of Line Analysis
**Learning:** For large file processing, a single-pass iteration with minimal string allocations is the most efficient approach. Consolidating metrics collection, secret detection, and duplication checks into one loop—while using early \`continue\` for blank lines—minimizes redundant work.
**Action:** Prioritize single-pass analysis over multiple passes with built-in functions like \`sum()\` when the per-element processing is already complex or requires multiple checks.
