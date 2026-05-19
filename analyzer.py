#!/usr/bin/env python3
"""
Code Quality Analyzer
A comprehensive Python code quality analysis tool

Usage:
    python analyzer.py --file <path_to_file.py>
    python analyzer.py --directory <path_to_directory>
"""

import ast
import os
import sys
import argparse
from typing import Dict, List, Optional
import re
import subprocess

try:
    import coverage
except ImportError:
    coverage = None


class CodeAnalysisVisitor(ast.NodeVisitor):
    """AST visitor to collect metrics in a single pass"""
    def __init__(self):
        self.functions = []
        self.classes_count = 0
        self.except_handlers = []
        self.try_nodes = []
        self.for_loops_with_append = set()
        self.for_stack = []
        self.dangerous_calls = []
        self.print_calls = []

    def visit_FunctionDef(self, node):
        self.functions.append(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes_count += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.except_handlers.append(node)
        self.generic_visit(node)

    def visit_Try(self, node):
        self.try_nodes.append(node)
        self.generic_visit(node)

    def visit_For(self, node):
        self.for_stack.append(node)
        self.generic_visit(node)
        self.for_stack.pop()

    def visit_Call(self, node):
        # Check for dangerous functions
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec']:
                self.dangerous_calls.append(node)
            elif node.func.id == 'print':
                self.print_calls.append(node)

        # Check for list comprehension opportunities
        if self.for_stack and isinstance(node.func, ast.Attribute) and node.func.attr == 'append':
            for for_node in self.for_stack:
                self.for_loops_with_append.add(for_node)

        self.generic_visit(node)


class CodeQualityAnalyzer:
    """Analyzes Python code for quality metrics and issues"""
    
    def __init__(self, file_path: str):
        self.file_path = os.path.abspath(file_path)
        self.file_name = os.path.basename(file_path)
        self.issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        self.metrics = {
            'lines_of_code': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'functions': 0,
            'classes': 0,
            'complexity': 0,
            'max_function_length': 0,
            'avg_function_length': 0,
            'coverage': None
        }
        self.scores = {
            'structure': 0,
            'error_handling': 0,
            'performance': 0,
            'security': 0,
            'maintainability': 0,
            'best_practices': 0
        }
        # Pre-compile secret detection regex for performance
        self.secret_re = re.compile(r'(password|api_key|secret|token)\s*=\s*["\'].*["\']', re.IGNORECASE)
        
    def analyze(self, test_file: Optional[str] = None) -> Dict:
        """Run complete analysis"""
        print(f"🔍 Analyzing {self.file_name}...")
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.code = f.read()
            self.lines = self.code.split('\n')
        
        # Parse AST
        try:
            self.tree = ast.parse(self.code)
        except SyntaxError as e:
            self.issues['critical'].append({
                'line': e.lineno,
                'issue': 'Syntax Error',
                'description': str(e),
                'severity': 'CRITICAL',
                'suggestion': 'Fix the syntax error to enable further analysis.'
            })
            return self.generate_report()
        
        # Consolidate AST traversal
        self.visitor = CodeAnalysisVisitor()
        self.visitor.visit(self.tree)

        # Run all analyses
        self._analyze_metrics()
        self._analyze_structure()
        self._analyze_error_handling()
        self._analyze_performance()
        self._analyze_security()
        self._analyze_maintainability()
        self._analyze_best_practices()
        
        # Run coverage if requested
        if test_file:
            self._run_coverage(test_file)

        # Calculate overall score
        self._calculate_scores()
        
        return self.generate_report()
    
    def _run_coverage(self, test_file: str):
        """Run tests and collect coverage data"""
        if not coverage:
            print("⚠️  Warning: 'coverage' package not installed. Skipping coverage analysis.")
            return

        print(f"🧪 Running coverage for {test_file}...")

        cov = coverage.Coverage(source=[os.path.dirname(self.file_path)])
        cov.start()

        try:
            # Run the test file as a script
            # We use subprocess to run it in a separate process to avoid conflicts
            # but then we won't get the coverage in this process easily.
            # Actually, we can run it using exec() or similar, but subprocess is safer.
            # Coverage can also be run via subprocess.

            # Resetting for simplicity: run coverage in a separate process and read output
            # Or use the API if we can run the test file here.

            # Simple approach: use the coverage API to run the test file
            import unittest
            loader = unittest.TestLoader()
            if os.path.isfile(test_file):
                # If it's a file, we might need to handle imports
                # Adding current dir to path
                sys.path.append(os.getcwd())
                sys.path.append(os.path.dirname(os.path.abspath(test_file)))

                module_name = os.path.basename(test_file).replace('.py', '')
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(module_name, test_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    suite = loader.loadTestsFromModule(module)
                    unittest.TextTestRunner(verbosity=0).run(suite)
                except Exception as e:
                    print(f"⚠️  Error running tests: {e}")

        finally:
            cov.stop()
            cov.save()

            # Get coverage for the specific file
            try:
                # coverage report doesn't easily return a dict, but we can use the API
                # Data is in .coverage file now
                # Re-load if needed, but it should be in cov
                analysis = cov._analyze(self.file_path)
                # analysis.numbers is a namedtuple: (total_statements, executed_statements, excluded_statements, missing_statements, pc_covered, pc_covered_str)
                self.metrics['coverage'] = analysis.numbers.pc_covered
            except Exception as e:
                print(f"⚠️  Error analyzing coverage: {e}")

    def _analyze_metrics(self):
        """Calculate basic code metrics"""
        self.metrics['lines_of_code'] = len(self.lines)
        
        for line in self.lines:
            stripped = line.strip()
            if not stripped:
                self.metrics['blank_lines'] += 1
            elif stripped.startswith('#'):
                self.metrics['comment_lines'] += 1
        
        # Count functions and classes from visitor
        self.metrics['functions'] = len(self.visitor.functions)
        self.metrics['classes'] = self.visitor.classes_count
    
    def _analyze_structure(self):
        """Analyze code structure"""
        score = 10.0
        
        # Check function lengths from visitor
        function_lengths = []
        for node in self.visitor.functions:
            length = node.end_lineno - node.lineno
            function_lengths.append(length)

            if length > 100:
                self.issues['high'].append({
                    'line': node.lineno,
                    'issue': 'Long Function',
                    'description': f"Function '{node.name}' is {length} lines (>100)",
                    'severity': 'HIGH',
                    'suggestion': f"Refactor '{node.name}' into smaller, more focused functions."
                })
                score -= 1.0
            elif length > 50:
                self.issues['medium'].append({
                    'line': node.lineno,
                    'issue': 'Long Function',
                    'description': f"Function '{node.name}' is {length} lines (>50)",
                    'severity': 'MEDIUM',
                    'suggestion': f"Consider breaking down '{node.name}' to improve readability."
                })
                score -= 0.5
        
        if function_lengths:
            self.metrics['max_function_length'] = max(function_lengths)
            self.metrics['avg_function_length'] = sum(function_lengths) / len(function_lengths)
        
        # Check for code duplication (simple check)
        if self._check_duplication():
            self.issues['medium'].append({
                'line': 0,
                'issue': 'Code Duplication',
                'description': 'Potential code duplication detected',
                'severity': 'MEDIUM',
                'suggestion': 'Extract common logic into reusable functions or classes (DRY principle).'
            })
            score -= 1.0
        
        self.scores['structure'] = max(0, score)
    
    def _analyze_error_handling(self):
        """Analyze error handling"""
        score = 10.0
        
        # Check for bare except clauses from visitor
        for node in self.visitor.except_handlers:
            if node.type is None:
                self.issues['high'].append({
                    'line': node.lineno,
                    'issue': 'Bare Except Clause',
                    'description': 'Using bare except: catches all exceptions including system exits',
                    'severity': 'HIGH',
                    'suggestion': 'Catch specific exceptions (e.g., ValueError, KeyError) instead of using a bare except.'
                })
                score -= 2.0
        
        # Check for try/except coverage from visitor
        try_count = len(self.visitor.try_nodes)
        if try_count == 0 and self.metrics['functions'] > 0:
            self.issues['medium'].append({
                'line': 0,
                'issue': 'No Error Handling',
                'description': 'No try/except blocks found',
                'severity': 'MEDIUM',
                'suggestion': 'Implement try/except blocks for operations that may fail (e.g., I/O, API calls).'
            })
            score -= 2.0
        
        self.scores['error_handling'] = max(0, score)
    
    def _analyze_performance(self):
        """Analyze performance patterns"""
        score = 10.0
        
        # Check for list comprehension opportunities from visitor
        for node in self.visitor.for_loops_with_append:
            self.issues['low'].append({
                'line': node.lineno,
                'issue': 'List Comprehension Opportunity',
                'description': 'Consider using list comprehension',
                'severity': 'LOW',
                'suggestion': 'Replace this for loop with a list comprehension for more concise and efficient code.'
            })
            score -= 0.3
        
        self.scores['performance'] = max(0, score)
    
    def _analyze_security(self):
        """Analyze security issues"""
        score = 10.0
        
        # Check for hardcoded secrets using optimized regex
        for i, line in enumerate(self.lines, 1):
            if self.secret_re.search(line):
                self.issues['critical'].append({
                    'line': i,
                    'issue': 'Hardcoded Secret',
                    'description': 'Potential hardcoded secret found',
                    'severity': 'CRITICAL',
                    'suggestion': 'Move secrets to environment variables or a secure secret manager.'
                })
                score -= 3.0
        
        # Check for eval/exec usage from visitor
        for node in self.visitor.dangerous_calls:
            self.issues['critical'].append({
                'line': node.lineno,
                'issue': 'Dangerous Function',
                'description': f'Use of {node.func.id}() is dangerous',
                'severity': 'CRITICAL',
                'suggestion': f"Avoid using {node.func.id}(). Use safer alternatives like ast.literal_eval() if needed."
            })
            score -= 3.0
        
        self.scores['security'] = max(0, score)
    
    def _analyze_maintainability(self):
        """Analyze code maintainability"""
        score = 10.0
        
        # Check for docstrings from visitor
        functions_with_docs = 0
        total_functions = len(self.visitor.functions)
        
        for node in self.visitor.functions:
            if ast.get_docstring(node):
                functions_with_docs += 1
        
        if total_functions > 0:
            doc_coverage = (functions_with_docs / total_functions) * 100
            if doc_coverage < 50:
                self.issues['medium'].append({
                    'line': 0,
                    'issue': 'Low Documentation',
                    'description': f'Only {doc_coverage:.0f}% of functions have docstrings',
                    'severity': 'MEDIUM',
                    'suggestion': 'Add docstrings to all public functions and classes to improve maintainability.'
                })
                score -= 2.0
        
        # Check for type hints from visitor
        functions_with_hints = 0
        for node in self.visitor.functions:
            if node.returns or any(arg.annotation for arg in node.args.args):
                functions_with_hints += 1
        
        if total_functions > 0:
            hint_coverage = (functions_with_hints / total_functions) * 100
            if hint_coverage < 30:
                self.issues['low'].append({
                    'line': 0,
                    'issue': 'Missing Type Hints',
                    'description': f'Only {hint_coverage:.0f}% of functions have type hints',
                    'severity': 'LOW',
                    'suggestion': 'Use type hints to improve code clarity and catch potential type errors early.'
                })
                score -= 1.0
        
        self.scores['maintainability'] = max(0, score)
    
    def _analyze_best_practices(self):
        """Analyze Python best practices"""
        score = 10.0
        
        # Check for print statements from visitor
        for node in self.visitor.print_calls:
            self.issues['low'].append({
                'line': node.lineno,
                'issue': 'Print Statement',
                'description': 'Consider using logging instead of print()',
                'severity': 'LOW',
                'suggestion': 'Use the logging module which provides better control over log levels and outputs.'
            })
            score -= 0.2
        
        # Check for proper naming conventions from visitor
        for node in self.visitor.functions:
            if not node.name.islower() and node.name != '__init__':
                self.issues['low'].append({
                    'line': node.lineno,
                    'issue': 'Naming Convention',
                    'description': f"Function '{node.name}' should use snake_case",
                    'severity': 'LOW',
                    'suggestion': f"Rename '{node.name}' to use snake_case (e.g., '{re.sub(r'(?<!^)(?=[A-Z])', '_', node.name).lower()}')."
                })
                score -= 0.3
        
        self.scores['best_practices'] = max(0, score)
    
    def _check_duplication(self) -> bool:
        """Simple duplication check"""
        # Check for repeated lines (simple heuristic)
        line_counts = {}
        for line in self.lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and len(stripped) > 20:
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        return any(count > 2 for count in line_counts.values())
    
    def _calculate_scores(self):
        """Calculate overall quality score"""
        weights = {
            'structure': 0.20,
            'error_handling': 0.20,
            'performance': 0.15,
            'security': 0.15,
            'maintainability': 0.15,
            'best_practices': 0.15
        }
        
        self.overall_score = sum(
            self.scores[category] * weight 
            for category, weight in weights.items()
        )

        # Bonus/Penalty for coverage if available
        if self.metrics['coverage'] is not None:
            # High coverage gives a small bonus, low coverage a penalty
            coverage_impact = (self.metrics['coverage'] - 70) / 100 # -0.7 to 0.3
            self.overall_score = max(0, min(10, self.overall_score + coverage_impact))
    
    def generate_report(self) -> Dict:
        """Generate analysis report"""
        return {
            'file': self.file_name,
            'overall_score': round(self.overall_score, 1),
            'category_scores': self.scores,
            'metrics': self.metrics,
            'issues': self.issues,
            'total_issues': sum(len(issues) for issues in self.issues.values())
        }
    
    def print_report(self, report: Dict):
        """Print formatted report"""
        use_color = sys.stdout.isatty()
        c = lambda t, s: f"\033[{s}m{t}\033[0m" if use_color else t

        print("\n" + c("="*80, "1;36"))
        print(c(f"📊 CODE QUALITY REPORT - {report['file']}", "1;36"))
        print(c("="*80, "1;36"))
        
        # Overall Score
        score = report['overall_score']
        rating = self._get_rating(score)
        sc = "92" if score >= 9 else ("93" if score >= 7 else "91")
        print(f"\n🎯 Overall Quality Score: {c(f'{score}/10', '1;' + sc)} {rating}")
        
        # Category Scores
        print(f"\n{c('📈 Category Scores:', '1')}")
        for cat, cs in report['category_scores'].items():
            csc = "92" if cs >= 9 else ("93" if cs >= 7 else "91")
            print(f"  - {cat.replace('_', ' ').title()}: {c(f'{cs:.1f}/10', csc)}")
        
        # Metrics
        print("\n📏 Code Metrics:")
        print(f"  - Lines of Code: {report['metrics']['lines_of_code']}")
        print(f"  - Functions: {report['metrics']['functions']}")
        print(f"  - Classes: {report['metrics']['classes']}")
        if report['metrics']['avg_function_length'] > 0:
            print(f"  - Avg Function Length: {report['metrics']['avg_function_length']:.1f} lines")
        if report['metrics']['coverage'] is not None:
            print(f"  - Test Coverage: {report['metrics']['coverage']:.1f}%")
        
        # Issues
        sev_c = {'critical': '1;91', 'high': '91', 'medium': '93', 'low': '96'}
        print(f"\n{c(f'🐛 Issues Found: {report['total_issues']}', '1')}")
        for severity in ['critical', 'high', 'medium', 'low']:
            issues = report['issues'][severity]
            if issues:
                print(f"\n  {c(severity.upper(), sev_c[severity])} ({len(issues)}):")
                for issue in issues[:5]:
                    li = f"Line {issue['line']}: " if issue['line'] > 0 else ""
                    print(f"    - {c(li + issue['issue'], '1')}\n      {issue['description']}")
                    if issue['line'] > 0 and 0 < issue['line'] <= len(self.lines):
                        snip = self.lines[issue['line']-1].strip()
                        if snip: print(f"      {c('> ' + snip, '2')}")
                print(f"\n  {severity.upper()} ({len(issues)}):")
                for issue in issues[:5]:  # Show first 5
                    line_info = f"Line {issue['line']}: " if issue['line'] > 0 else ""
                    print(f"    - {line_info}{issue['issue']}")
                    print(f"      {issue['description']}")
                    if 'suggestion' in issue:
                        print(f"      💡 Suggestion: {issue['suggestion']}")
                if len(issues) > 5:
                    print(f"    ... and {len(issues) - 5} more")
        
        # Production Readiness
        print("\n" + c("="*80, "1;36"))
        if score >= 9.0 and not report['issues']['critical']:
            print(c("✅ PRODUCTION READY - Excellent code quality!", "1;92"))
        elif score >= 7.0 and not report['issues']['critical']:
            print(c("✅ PRODUCTION READY - Good code quality with minor improvements needed", "92"))
        elif report['issues']['critical']:
            print(c("❌ NOT PRODUCTION READY - Critical issues must be fixed", "1;91"))
        else:
            print("⚠️  NEEDS IMPROVEMENT - Significant refactoring recommended")
        print("="*80 + "\n")

    def generate_markdown_report(self, report: Dict) -> str:
        """Generate detailed Markdown report"""
        md = f"# 📊 Code Quality Report - {report['file']}\n\n"

        score = report['overall_score']
        rating = self._get_rating(score)
        md += f"## 🎯 Executive Summary\n\n"
        md += f"| Category | Rating | Score |\n"
        md += f"|----------|--------|-------|\n"
        md += f"| **Overall Quality** | {rating} | {score}/10 |\n"
        for cat, s in report['category_scores'].items():
            md += f"| {cat.replace('_', ' ').title()} | {self._get_rating(s)} | {s:.1f}/10 |\n"

        md += f"\n**Verdict**: "
        if score >= 9.0 and report['issues']['critical'] == []:
            md += "✅ **PRODUCTION READY** - Excellent code quality!\n\n"
        elif score >= 7.0 and report['issues']['critical'] == []:
            md += "✅ **PRODUCTION READY** - Good code quality with minor improvements needed\n\n"
        elif report['issues']['critical']:
            md += "❌ **NOT PRODUCTION READY** - Critical issues must be fixed\n\n"
        else:
            md += "⚠️  **NEEDS IMPROVEMENT** - Significant refactoring recommended\n\n"

        md += "## 📏 Code Metrics\n\n"
        md += f"- **Lines of Code**: {report['metrics']['lines_of_code']}\n"
        md += f"- **Functions**: {report['metrics']['functions']}\n"
        md += f"- **Classes**: {report['metrics']['classes']}\n"
        if report['metrics']['avg_function_length'] > 0:
            md += f"- **Avg Function Length**: {report['metrics']['avg_function_length']:.1f} lines\n"
        if report['metrics']['coverage'] is not None:
            md += f"- **Test Coverage**: {report['metrics']['coverage']:.1f}%\n"

        md += f"\n## 🐛 Issues Found ({report['total_issues']})\n\n"

        for severity in ['critical', 'high', 'medium', 'low']:
            issues = report['issues'][severity]
            if issues:
                md += f"### 🔴 {severity.upper()} ({len(issues)})\n\n"
                for issue in issues:
                    line_info = f"Line {issue['line']}: " if issue['line'] > 0 else ""
                    md += f"- **{line_info}{issue['issue']}**\n"
                    md += f"  - *Problem*: {issue['description']}\n"
                    if 'suggestion' in issue:
                        md += f"  - *Fix*: {issue['suggestion']}\n"
                md += "\n"

        md += "## 💡 Recommendations\n\n"
        all_issues = []
        for s in ['critical', 'high', 'medium', 'low']:
            all_issues.extend(report['issues'][s])

        if not all_issues:
            md += "Keep up the great work! No major issues found.\n"
        else:
            # Sort by severity
            for i, issue in enumerate(all_issues[:10]): # Top 10 recommendations
                md += f"{i+1}. **{issue['issue']}**: {issue['suggestion']}\n"

        return md

    def generate_llm_prompt(self, report: Dict) -> str:
        """Generate a prompt for LLM enrichment"""
        prompt = "Act as an expert Python software engineer. Review the following code and its quality analysis report.\n"
        prompt += "Provide a detailed code review, explaining why each issue is problematic and providing refactored code snippets.\n\n"

        prompt += "### CODE TO REVIEW\n"
        prompt += "```python\n"
        prompt += self.code
        prompt += "\n```\n\n"

        prompt += "### ANALYSIS REPORT SUMMARY\n"
        prompt += f"- Overall Score: {report['overall_score']}/10\n"
        prompt += f"- Total Issues: {report['total_issues']}\n"

        prompt += "\n### ISSUES FOUND\n"
        for severity in ['critical', 'high', 'medium', 'low']:
            issues = report['issues'][severity]
            if issues:
                prompt += f"#### {severity.upper()}\n"
                for issue in issues:
                    line_info = f" (Line {issue['line']})" if issue['line'] > 0 else ""
                    prompt += f"- {issue['issue']}{line_info}: {issue['description']}\n"

        prompt += "\n### INSTRUCTIONS\n"
        prompt += "1. Analyze the critical and high priority issues first.\n"
        prompt += "2. Suggest concrete refactoring for the identified issues.\n"
        prompt += "3. Identify any subtle bugs or architectural issues not caught by the automated tool.\n"
        prompt += "4. Provide the final, improved version of the code.\n"

        return prompt
    
    def _get_rating(self, score: float) -> str:
        """Get star rating"""
        if score >= 9.0:
            return "⭐⭐⭐⭐⭐"
        elif score >= 7.0:
            return "⭐⭐⭐⭐☆"
        elif score >= 5.0:
            return "⭐⭐⭐☆☆"
        elif score >= 3.0:
            return "⭐⭐☆☆☆"
        else:
            return "⭐☆☆☆☆"


def main():
    parser = argparse.ArgumentParser(description='Analyze Python code quality')
    parser.add_argument('--file', type=str, help='Path to Python file to analyze')
    parser.add_argument('--directory', type=str, help='Path to directory to analyze')
    parser.add_argument('--output', type=str, help='Output report file (optional)')
    parser.add_argument('--test-file', type=str, help='Path to test file for coverage analysis')
    parser.add_argument('--llm-prompt', action='store_true', help='Generate LLM enrichment prompt')
    
    args = parser.parse_args()
    
    if not args.file and not args.directory:
        parser.print_help()
        sys.exit(1)
    
    files_to_analyze = []
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ Error: File not found: {args.file}")
            sys.exit(1)
        files_to_analyze.append(args.file)
    
    if args.directory:
        if not os.path.exists(args.directory):
            print(f"❌ Error: Directory not found: {args.directory}")
            sys.exit(1)
        for root, dirs, files in os.walk(args.directory):
            for file in files:
                if file.endswith('.py'):
                    files_to_analyze.append(os.path.join(root, file))
    
    print(f"\n🔍 Analyzing {len(files_to_analyze)} file(s)...\n")
    
    for file_path in files_to_analyze:
        analyzer = CodeQualityAnalyzer(file_path)
        report = analyzer.analyze(test_file=args.test_file)

        if args.llm_prompt:
            print("\n" + "="*80)
            print("🤖 LLM ENRICHMENT PROMPT")
            print("="*80)
            print(analyzer.generate_llm_prompt(report))
            print("="*80 + "\n")
        else:
            analyzer.print_report(report)

        if args.output:
            md_report = analyzer.generate_markdown_report(report)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(md_report)
            print(f"📝 Report saved to {args.output}")


if __name__ == "__main__":
    main()
