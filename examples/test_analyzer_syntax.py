import unittest
import sys
import os

# Add root to sys.path to import analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyzer import CodeQualityAnalyzer

class TestAnalyzerSyntax(unittest.TestCase):
    def test_syntax_error_handling(self):
        invalid_file = os.path.join(os.path.dirname(__file__), 'invalid_syntax.py')
        analyzer = CodeQualityAnalyzer(invalid_file)
        report = analyzer.analyze()

        # Check if syntax error is in critical issues
        critical_issues = report['issues']['critical']
        self.assertTrue(any(issue['issue'] == 'Syntax Error' for issue in critical_issues), "Syntax Error not found in critical issues")

        # Verify specific details
        syntax_error = next(issue for issue in critical_issues if issue['issue'] == 'Syntax Error')
        self.assertEqual(syntax_error['line'], 1)
        self.assertEqual(syntax_error['severity'], 'CRITICAL')
        self.assertIn("Fix the syntax error", syntax_error['suggestion'])

if __name__ == '__main__':
    unittest.main()
