import unittest
import ast
import sys
import os

# Add the parent directory to sys.path to import analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyzer import CodeAnalysisVisitor

class TestCodeAnalysisVisitor(unittest.TestCase):
    def setUp(self):
        self.visitor = CodeAnalysisVisitor()

    def analyze_code(self, code):
        tree = ast.parse(code)
        self.visitor.visit(tree)

    def test_visit_call_eval_exec(self):
        code = "eval('1+1'); exec('print(1)')"
        self.analyze_code(code)

        dangerous_names = [name for node, name in self.visitor.dangerous_calls]
        self.assertIn('eval', dangerous_names)
        self.assertIn('exec', dangerous_names)
        self.assertEqual(len(self.visitor.dangerous_calls), 2)

    def test_visit_call_print(self):
        code = "print('hello world')"
        self.analyze_code(code)

        self.assertEqual(len(self.visitor.print_calls), 1)
        self.assertIsInstance(self.visitor.print_calls[0], ast.Call)

    def test_visit_call_os_dangerous(self):
        code = "import os; os.system('ls'); os.popen('whoami')"
        self.analyze_code(code)

        dangerous_names = [name for node, name in self.visitor.dangerous_calls]
        self.assertIn('os.system', dangerous_names)
        self.assertIn('os.popen', dangerous_names)

    def test_visit_call_subprocess_shell_true(self):
        code = "import subprocess; subprocess.run('ls', shell=True)"
        self.analyze_code(code)

        dangerous_names = [name for node, name in self.visitor.dangerous_calls]
        self.assertIn('subprocess.run', dangerous_names)

    def test_visit_call_subprocess_shell_false(self):
        code = "import subprocess; subprocess.run(['ls'], shell=False)"
        self.analyze_code(code)

        dangerous_names = [name for node, name in self.visitor.dangerous_calls]
        self.assertNotIn('subprocess.run', dangerous_names)

    def test_visit_call_insecure_deserialization(self):
        code = "import pickle, marshal; pickle.load(f); marshal.loads(b)"
        self.analyze_code(code)

        dangerous_names = [name for node, name in self.visitor.dangerous_calls]
        self.assertIn('pickle.load', dangerous_names)
        self.assertIn('marshal.loads', dangerous_names)

    def test_visit_call_list_comprehension_opportunity(self):
        code = """
results = []
for x in range(10):
    results.append(x * 2)
"""
        self.analyze_code(code)

        self.assertEqual(len(self.visitor.for_loops_with_append), 1)
        # The node in for_loops_with_append should be the For node
        for_node = self.visitor.for_loops_with_append.pop()
        self.assertIsInstance(for_node, ast.For)

    def test_visit_call_attribute_no_name_value(self):
        # Test case for when func.value is not an ast.Name (e.g. (f()).append(x))
        code = "get_list().append(x)"
        self.analyze_code(code)
        # Should not crash and should not be identified as list comp opportunity if not in for loop
        self.assertEqual(len(self.visitor.for_loops_with_append), 0)

if __name__ == '__main__':
    unittest.main()
