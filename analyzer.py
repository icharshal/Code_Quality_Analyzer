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
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import re


class CodeQualityAnalyzer:
    """Analyzes Python code for quality metrics and issues"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
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
            'avg_function_length': 0
        }
        self.scores = {
            'structure': 0,
            'error_handling': 0,
            'performance': 0,
            'security': 0,
            'maintainability': 0,
            'best_practices': 0
        }
        
    def analyze(self) -> Dict:
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
                'severity': 'CRITICAL'
            })
            return self.generate_report()
        
        # Run all analyses
        self._analyze_metrics()
        self._analyze_structure()
        self._analyze_error_handling()
        self._analyze_performance()
        self._analyze_security()
        self._analyze_maintainability()
        self._analyze_best_practices()
        
        # Calculate overall score
        self._calculate_scores()
        
        return self.generate_report()
    
    def _analyze_metrics(self):
        """Calculate basic code metrics"""
        self.metrics['lines_of_code'] = len(self.lines)
        
        for line in self.lines:
            stripped = line.strip()
            if not stripped:
                self.metrics['blank_lines'] += 1
            elif stripped.startswith('#'):
                self.metrics['comment_lines'] += 1
        
        # Count functions and classes
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self.metrics['functions'] += 1
            elif isinstance(node, ast.ClassDef):
                self.metrics['classes'] += 1
    
    def _analyze_structure(self):
        """Analyze code structure"""
        score = 10.0
        
        # Check function lengths
        function_lengths = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                length = node.end_lineno - node.lineno
                function_lengths.append(length)
                
                if length > 100:
                    self.issues['high'].append({
                        'line': node.lineno,
                        'issue': 'Long Function',
                        'description': f"Function '{node.name}' is {length} lines (>100)",
                        'severity': 'HIGH'
                    })
                    score -= 1.0
                elif length > 50:
                    self.issues['medium'].append({
                        'line': node.lineno,
                        'issue': 'Long Function',
                        'description': f"Function '{node.name}' is {length} lines (>50)",
                        'severity': 'MEDIUM'
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
                'severity': 'MEDIUM'
            })
            score -= 1.0
        
        self.scores['structure'] = max(0, score)
    
    def _analyze_error_handling(self):
        """Analyze error handling"""
        score = 10.0
        
        # Check for bare except clauses
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.issues['high'].append({
                        'line': node.lineno,
                        'issue': 'Bare Except Clause',
                        'description': 'Using bare except: catches all exceptions including system exits',
                        'severity': 'HIGH'
                    })
                    score -= 2.0
        
        # Check for try/except coverage
        try_count = sum(1 for node in ast.walk(self.tree) if isinstance(node, ast.Try))
        if try_count == 0 and self.metrics['functions'] > 0:
            self.issues['medium'].append({
                'line': 0,
                'issue': 'No Error Handling',
                'description': 'No try/except blocks found',
                'severity': 'MEDIUM'
            })
            score -= 2.0
        
        self.scores['error_handling'] = max(0, score)
    
    def _analyze_performance(self):
        """Analyze performance patterns"""
        score = 10.0
        
        # Check for inefficient patterns
        for node in ast.walk(self.tree):
            # Check for list comprehension opportunities
            if isinstance(node, ast.For):
                # Simple heuristic: for loop with append
                if any(isinstance(child, ast.Expr) and 
                       isinstance(child.value, ast.Call) and
                       isinstance(child.value.func, ast.Attribute) and
                       child.value.func.attr == 'append'
                       for child in ast.walk(node)):
                    self.issues['low'].append({
                        'line': node.lineno,
                        'issue': 'List Comprehension Opportunity',
                        'description': 'Consider using list comprehension',
                        'severity': 'LOW'
                    })
                    score -= 0.3
        
        self.scores['performance'] = max(0, score)
    
    def _analyze_security(self):
        """Analyze security issues"""
        score = 10.0
        
        # Check for hardcoded secrets (simple patterns)
        secret_patterns = [
            r'password\s*=\s*["\'].*["\']',
            r'api_key\s*=\s*["\'].*["\']',
            r'secret\s*=\s*["\'].*["\']',
            r'token\s*=\s*["\'].*["\']'
        ]
        
        for i, line in enumerate(self.lines, 1):
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues['critical'].append({
                        'line': i,
                        'issue': 'Hardcoded Secret',
                        'description': 'Potential hardcoded secret found',
                        'severity': 'CRITICAL'
                    })
                    score -= 3.0
        
        # Check for eval/exec usage
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        self.issues['critical'].append({
                            'line': node.lineno,
                            'issue': 'Dangerous Function',
                            'description': f'Use of {node.func.id}() is dangerous',
                            'severity': 'CRITICAL'
                        })
                        score -= 3.0
        
        self.scores['security'] = max(0, score)
    
    def _analyze_maintainability(self):
        """Analyze code maintainability"""
        score = 10.0
        
        # Check for docstrings
        functions_with_docs = 0
        total_functions = 0
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if ast.get_docstring(node):
                    functions_with_docs += 1
        
        if total_functions > 0:
            doc_coverage = (functions_with_docs / total_functions) * 100
            if doc_coverage < 50:
                self.issues['medium'].append({
                    'line': 0,
                    'issue': 'Low Documentation',
                    'description': f'Only {doc_coverage:.0f}% of functions have docstrings',
                    'severity': 'MEDIUM'
                })
                score -= 2.0
        
        # Check for type hints
        functions_with_hints = 0
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    functions_with_hints += 1
        
        if total_functions > 0:
            hint_coverage = (functions_with_hints / total_functions) * 100
            if hint_coverage < 30:
                self.issues['low'].append({
                    'line': 0,
                    'issue': 'Missing Type Hints',
                    'description': f'Only {hint_coverage:.0f}% of functions have type hints',
                    'severity': 'LOW'
                })
                score -= 1.0
        
        self.scores['maintainability'] = max(0, score)
    
    def _analyze_best_practices(self):
        """Analyze Python best practices"""
        score = 10.0
        
        # Check for print statements (should use logging)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    self.issues['low'].append({
                        'line': node.lineno,
                        'issue': 'Print Statement',
                        'description': 'Consider using logging instead of print()',
                        'severity': 'LOW'
                    })
                    score -= 0.2
        
        # Check for proper naming conventions
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower() and node.name != '__init__':
                    self.issues['low'].append({
                        'line': node.lineno,
                        'issue': 'Naming Convention',
                        'description': f"Function '{node.name}' should use snake_case",
                        'severity': 'LOW'
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
        print("\n" + "="*80)
        print(f"📊 CODE QUALITY REPORT - {report['file']}")
        print("="*80)
        
        # Overall Score
        score = report['overall_score']
        rating = self._get_rating(score)
        print(f"\n🎯 Overall Quality Score: {score}/10 {rating}")
        
        # Category Scores
        print("\n📈 Category Scores:")
        for category, score in report['category_scores'].items():
            print(f"  - {category.replace('_', ' ').title()}: {score:.1f}/10")
        
        # Metrics
        print("\n📏 Code Metrics:")
        print(f"  - Lines of Code: {report['metrics']['lines_of_code']}")
        print(f"  - Functions: {report['metrics']['functions']}")
        print(f"  - Classes: {report['metrics']['classes']}")
        if report['metrics']['avg_function_length'] > 0:
            print(f"  - Avg Function Length: {report['metrics']['avg_function_length']:.1f} lines")
        
        # Issues
        print(f"\n🐛 Issues Found: {report['total_issues']}")
        for severity in ['critical', 'high', 'medium', 'low']:
            issues = report['issues'][severity]
            if issues:
                print(f"\n  {severity.upper()} ({len(issues)}):")
                for issue in issues[:5]:  # Show first 5
                    line_info = f"Line {issue['line']}: " if issue['line'] > 0 else ""
                    print(f"    - {line_info}{issue['issue']}")
                    print(f"      {issue['description']}")
                if len(issues) > 5:
                    print(f"    ... and {len(issues) - 5} more")
        
        # Production Readiness
        print("\n" + "="*80)
        if score >= 9.0 and report['issues']['critical'] == []:
            print("✅ PRODUCTION READY - Excellent code quality!")
        elif score >= 7.0 and report['issues']['critical'] == []:
            print("✅ PRODUCTION READY - Good code quality with minor improvements needed")
        elif report['issues']['critical']:
            print("❌ NOT PRODUCTION READY - Critical issues must be fixed")
        else:
            print("⚠️  NEEDS IMPROVEMENT - Significant refactoring recommended")
        print("="*80 + "\n")
    
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
        report = analyzer.analyze()
        analyzer.print_report(report)


if __name__ == "__main__":
    main()
