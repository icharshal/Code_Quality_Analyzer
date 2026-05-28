import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch
import sys

# Add the parent directory to sys.path to import analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyzer import CodeQualityAnalyzer

class TestCodeQualityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_test_file(self, content, filename="test_file.py"):
        path = os.path.join(self.test_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_analyze_valid_code(self):
        code = """
def hello_world():
    \"\"\"Docstring\"\"\"
    print("Hello")
"""
        path = self.create_test_file(code)
        analyzer = CodeQualityAnalyzer(path)
        report = analyzer.analyze()

        self.assertEqual(report['file'], "test_file.py")
        self.assertIn('overall_score', report)
        self.assertIn('metrics', report)
        self.assertEqual(report['metrics']['functions'], 1)
        # Issues might include: Print statement, Low documentation, Missing type hints etc.
        # So we just check that it's greater than 0
        self.assertGreater(report['total_issues'], 0)

    def test_analyze_syntax_error(self):
        code = "def invalid_syntax("
        path = self.create_test_file(code)
        analyzer = CodeQualityAnalyzer(path)
        report = analyzer.analyze()

        self.assertEqual(report['total_issues'], 1)
        self.assertEqual(report['issues']['critical'][0]['issue'], 'Syntax Error')

    def test_analyze_secrets(self):
        code = "API_KEY = 'secret-token-123'"
        path = self.create_test_file(code)
        analyzer = CodeQualityAnalyzer(path)
        report = analyzer.analyze()

        critical_issues = [i['issue'] for i in report['issues']['critical']]
        self.assertIn('Hardcoded Secret', critical_issues)

    def test_analyze_long_function(self):
        lines = ["def long_func():"]
        lines.extend(["    print('line')" for _ in range(110)])
        code = "\n".join(lines)
        path = self.create_test_file(code)
        analyzer = CodeQualityAnalyzer(path)
        report = analyzer.analyze()

        high_issues = [i['issue'] for i in report['issues']['high']]
        self.assertIn('Long Function', high_issues)

    def test_analyze_bare_except(self):
        code = """
def fail():
    try:
        1/0
    except:
        pass
"""
        path = self.create_test_file(code)
        analyzer = CodeQualityAnalyzer(path)
        report = analyzer.analyze()

        high_issues = [i['issue'] for i in report['issues']['high']]
        self.assertIn('Bare Except Clause', high_issues)

    def test_analyze_dangerous_functions(self):
        code = "eval('1+1')"
        path = self.create_test_file(code)
        analyzer = CodeQualityAnalyzer(path)
        report = analyzer.analyze()

        critical_issues = [i['issue'] for i in report['issues']['critical']]
        self.assertIn('Dangerous Function', critical_issues)

    def test_analyze_naming_convention(self):
        code = "def BadName(): pass"
        path = self.create_test_file(code)
        analyzer = CodeQualityAnalyzer(path)
        report = analyzer.analyze()

        low_issues = [i['issue'] for i in report['issues']['low']]
        self.assertIn('Naming Convention', low_issues)

    def test_analyze_duplication(self):
        line = "print('This is a very long line that is duplicated')"
        code = "\n".join([line] * 5)
        path = self.create_test_file(code)
        analyzer = CodeQualityAnalyzer(path)
        report = analyzer.analyze()

        medium_issues = [i['issue'] for i in report['issues']['medium']]
        self.assertIn('Code Duplication', medium_issues)

    @patch('analyzer.coverage')
    def test_analyze_with_coverage(self, mock_coverage):
        if mock_coverage is None:
            self.skipTest("Coverage module not available even for mocking")

        code = "def add(a, b): return a + b"
        path = self.create_test_file(code)

        test_code = """
import unittest
from test_file import add
class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
"""
        test_path = self.create_test_file(test_code, "test_test_file.py")

        # Setup mock coverage
        mock_cov_instance = MagicMock()
        mock_coverage.Coverage.return_value = mock_cov_instance
        mock_analysis = MagicMock()
        mock_analysis.numbers.pc_covered = 100.0
        mock_cov_instance._analyze.return_value = mock_analysis

        analyzer = CodeQualityAnalyzer(path)
        with patch.object(analyzer, '_execute_tests'): # Don't actually run tests
            report = analyzer.analyze(test_file=test_path)

        self.assertEqual(report['metrics']['coverage'], 100.0)

if __name__ == '__main__':
    unittest.main()
