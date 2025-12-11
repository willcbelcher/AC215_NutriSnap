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
    
    # Mock GenerativeModel constructor
    with patch("gemini_utils.GenerativeModel", return_value=mock_model):
        # Also need to mock _init_vertex or vertexai.init to avoid errors if env vars missing
        with patch("gemini_utils.vertexai.init"):
            triggers = gemini_utils.get_food_triggers("ramen", b"fake_image")
            assert triggers == "Gluten, Soy"

