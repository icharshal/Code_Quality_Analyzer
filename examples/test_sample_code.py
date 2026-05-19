import unittest
from sample_code import calculate_sum

class TestCalculateSum(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(calculate_sum([]), 0)

    def test_positive_numbers(self):
        self.assertEqual(calculate_sum([1, 2, 3, 4, 5]), 15)

    def test_negative_numbers(self):
        self.assertEqual(calculate_sum([-1, -2, -3]), -6)

    def test_mixed_numbers(self):
        self.assertEqual(calculate_sum([-1, 1, 0]), 0)

    def test_large_list(self):
        numbers = list(range(1001))
        self.assertEqual(calculate_sum(numbers), sum(numbers))

if __name__ == '__main__':
    unittest.main()
