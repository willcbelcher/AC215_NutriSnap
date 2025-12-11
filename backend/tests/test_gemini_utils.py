import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import gemini_utils

def test_get_food_triggers_success():
    """Test successful trigger retrieval"""
    mock_response = MagicMock()
    mock_response.text = "Gluten, Soy"
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    with patch("gemini_utils.genai.GenerativeModel", return_value=mock_model):
        triggers = gemini_utils.get_food_triggers("ramen", b"fake_image")
        assert triggers == "Gluten, Soy"

def test_get_food_triggers_error():
    """Test error handling in trigger retrieval"""
    with patch("gemini_utils.genai.GenerativeModel", side_effect=Exception("API Error")):
        triggers = gemini_utils.get_food_triggers("ramen", b"fake_image")
        assert triggers == "None"
