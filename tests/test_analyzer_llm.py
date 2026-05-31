import unittest
from unittest.mock import patch, MagicMock
import json
import urllib.request
import urllib.error
import io
from analyzer import CodeQualityAnalyzer

class TestAnalyzerLLM(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeQualityAnalyzer("analyzer.py")
        self.report = {
            "file": "analyzer.py",
            "overall_score": 8.5,
            "total_issues": 3,
            "issues": {
                "critical": [],
                "high": [],
                "medium": [{"issue": "Test Issue", "line": 10, "description": "Test description"}],
                "low": []
            }
        }
        self.analyzer.code = "print('hello')" # Mock code for prompt generation

    @patch('urllib.request.urlopen')
    def test_get_llm_review_success(self, mock_urlopen):
        # Mock successful response
        mock_response = MagicMock()
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": "Mocked LLM Review Content"
                    }
                }
            ]
        }
        mock_response.read.return_value = json.dumps(response_data).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.analyzer.get_llm_review(self.report, "fake_key")

        self.assertEqual(result, "Mocked LLM Review Content")
        self.assertEqual(self.analyzer.llm_review, "Mocked LLM Review Content")
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen')
    def test_get_llm_review_timeout(self, mock_urlopen):
        # Mock timeout error
        mock_urlopen.side_effect = urllib.error.URLError("Timeout")

        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = self.analyzer.get_llm_review(self.report, "fake_key")

            self.assertIsNone(result)
            self.assertIn("Error fetching LLM review", fake_out.getvalue())

    @patch('urllib.request.urlopen')
    def test_get_llm_review_malformed_json(self, mock_urlopen):
        # Mock malformed JSON response
        mock_response = MagicMock()
        mock_response.read.return_value = b"invalid json"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = self.analyzer.get_llm_review(self.report, "fake_key")

            self.assertIsNone(result)
            self.assertIn("Error fetching LLM review", fake_out.getvalue())

    @patch('urllib.request.urlopen')
    def test_get_llm_review_missing_fields(self, mock_urlopen):
        # Mock JSON response missing expected fields
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"error": "not found"}).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            result = self.analyzer.get_llm_review(self.report, "fake_key")

            self.assertIsNone(result)
            self.assertIn("Error fetching LLM review", fake_out.getvalue())

if __name__ == '__main__':
    unittest.main()
