import unittest
from analyzer import CodeQualityAnalyzer
import os

class TestCodeQualityAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a dummy file for initialization
        self.dummy_file = 'dummy_test.py'
        with open(self.dummy_file, 'w') as f:
            f.write('# Dummy file')
        self.analyzer = CodeQualityAnalyzer(self.dummy_file)

    def tearDown(self):
        if os.path.exists(self.dummy_file):
            os.remove(self.dummy_file)

    def test_calculate_scores_basic(self):
        # Set scores to 10 for all categories
        for cat in self.analyzer.scores:
            self.analyzer.scores[cat] = 10.0

        self.analyzer._calculate_scores()
        # Weights: structure 0.2, error_handling 0.2, others 0.15
        # 10*0.2 + 10*0.2 + 10*0.15 + 10*0.15 + 10*0.15 + 10*0.15 = 2 + 2 + 1.5 + 1.5 + 1.5 + 1.5 = 10
        self.assertEqual(self.analyzer.overall_score, 10.0)

    def test_calculate_scores_with_coverage_bonus(self):
        # Set scores to 8 for all categories
        for cat in self.analyzer.scores:
            self.analyzer.scores[cat] = 8.0

        # Coverage 100% (bonus: (100-70)/100 = 0.3)
        self.analyzer.metrics['coverage'] = 100
        self.analyzer._calculate_scores()

        # Base score 8.0 + 0.3 = 8.3
        self.assertAlmostEqual(self.analyzer.overall_score, 8.3)

    def test_calculate_scores_with_coverage_penalty(self):
        # Set scores to 5 for all categories
        for cat in self.analyzer.scores:
            self.analyzer.scores[cat] = 5.0

        # Coverage 0% (penalty: (0-70)/100 = -0.7)
        self.analyzer.metrics['coverage'] = 0
        self.analyzer._calculate_scores()

        # Base score 5.0 - 0.7 = 4.3
        self.assertAlmostEqual(self.analyzer.overall_score, 4.3)

    def test_calculate_scores_clamping(self):
        # Test max clamping
        for cat in self.analyzer.scores:
            self.analyzer.scores[cat] = 10.0
        self.analyzer.metrics['coverage'] = 100
        self.analyzer._calculate_scores()
        self.assertEqual(self.analyzer.overall_score, 10.0)

        # Test min clamping
        for cat in self.analyzer.scores:
            self.analyzer.scores[cat] = 0.0
        self.analyzer.metrics['coverage'] = 0
        self.analyzer._calculate_scores()
        self.assertEqual(self.analyzer.overall_score, 0.0)

    def test_generate_report_structure(self):
        self.analyzer.overall_score = 8.567
        self.analyzer.issues['high'].append({'issue': 'Test Issue'})

        report = self.analyzer.generate_report()

        expected_keys = {
            'file', 'overall_score', 'category_scores',
            'metrics', 'issues', 'total_issues', 'llm_review'
        }
        self.assertTrue(expected_keys.issubset(report.keys()))

        # Verify rounding
        self.assertEqual(report['overall_score'], 8.6)

        # Verify total issues
        self.assertEqual(report['total_issues'], 1)

    def test_generate_report_total_issues(self):
        self.analyzer.overall_score = 7.0
        self.analyzer.issues['critical'].append({'issue': 'C1'})
        self.analyzer.issues['high'].append({'issue': 'H1'})
        self.analyzer.issues['medium'].append({'issue': 'M1'})
        self.analyzer.issues['low'].append({'issue': 'L1'})

        report = self.analyzer.generate_report()
        self.assertEqual(report['total_issues'], 4)

if __name__ == '__main__':
    unittest.main()
