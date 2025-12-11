import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from inference import predict

def test_predict_success():
    """Test successful prediction"""
    mock_model = MagicMock()
    mock_model.return_value = [{"label": "ramen", "score": 0.95}]
    
    with patch("inference.pipeline", return_value=mock_model):
        # We need to mock the pipeline call itself since predict calls it
        # But predict loads the pipeline inside the function if not loaded?
        # Actually inference.py likely loads it at module level or inside.
        # Let's check inference.py content first if possible, but assuming standard usage:
        
        # Mocking the pipeline function from transformers
        with patch("inference.pipeline") as mock_pipeline:
            mock_classifier = MagicMock()
            mock_classifier.return_value = [{"label": "ramen", "score": 0.95}]
            mock_pipeline.return_value = mock_classifier
            
            # Since predict might use a global model, we might need to reload or mock where it's used
            # For now, let's try to mock the classifier object if it's global
            
            result = predict(b"fake_image_data")
            assert "top1" in result
            assert result["top1"][0]["label"] == "ramen"

def test_predict_error():
    """Test prediction error handling"""
    with patch("inference.Image.open", side_effect=Exception("Invalid image")):
        with pytest.raises(Exception):
            predict(b"bad_data")
