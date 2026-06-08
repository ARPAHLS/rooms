import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import io

from rooms.ollama_preflight import run_ollama_preflight

class TestOllamaPreflightLogic(unittest.TestCase):
    def setUp(self):
        # Setup clean configuration mock structure
        self.mock_settings = MagicMock()
        self.mock_settings.defaults.litellm_model = "ollama/gemma4:e2b"
        self.mock_settings.ollama.base_url = "http://localhost:11434"

    def test_skips_non_ollama_models(self):
        self.mock_settings.defaults.litellm_model = "openai/gpt-4"
        result = run_ollama_preflight(self.mock_settings)
        self.assertTrue(result)

    @patch("urllib.request.urlopen")
    def test_preflight_success_exact_match(self, mock_urlopen):
        # Simulate clean API json payload back from Ollama
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"models": [{"name": "gemma4:e2b"}, {"name": "llama3:latest"}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = run_ollama_preflight(self.mock_settings)
        self.assertTrue(result)

    @patch("urllib.request.urlopen")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_preflight_missing_model_tag(self, mock_stdout, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"models": [{"name": "llama3:latest"}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = run_ollama_preflight(self.mock_settings)
        self.assertFalse(result)

    @patch("urllib.request.urlopen")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_preflight_server_unreachable(self, mock_stdout, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        
        result = run_ollama_preflight(self.mock_settings)
        self.assertFalse(result)