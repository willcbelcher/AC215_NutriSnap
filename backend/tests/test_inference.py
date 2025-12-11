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
    # Mock the bundle components
    mock_processor = MagicMock()
    mock_model = MagicMock()
    mock_device = "cpu"
    mock_id2label = {0: "ramen"}
    
    # Mock model output
    mock_logits = MagicMock()
    # Create a tensor for logits that will result in high probability for index 0
    # We need to mock torch.softmax return value effectively
    
    # Instead of mocking internal torch calls which is hard, let's mock the model call
    # But predict calls model(**inputs).logits
    
    # Easier approach: Mock get_bundle to return mocks, and mock torch.softmax/topk if possible
    # Or just mock the whole predict function? No, we want to test predict logic.
    
    # Let's mock get_bundle and the model behavior
    mock_bundle = {
        "processor": mock_processor,
        "model": mock_model,
        "device": mock_device,
        "id2label": mock_id2label
    }
    
    with patch("inference.get_bundle", return_value=mock_bundle):
        with patch("inference.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value.convert.return_value = MagicMock()
            
            # Mock processor return
            mock_processor.return_value = {"pixel_values": MagicMock()}
            
            # Mock model output
            mock_output = MagicMock()
            # We need to mock logits. But wait, predict uses torch.softmax on logits.
            # If we don't want to rely on real torch, we should mock torch too?
            # inference.py imports torch.
            
            # Let's just mock the torch.softmax and torch.topk calls inside inference.py
            # This avoids needing real tensors
            
            with patch("inference.torch.softmax") as mock_softmax:
                with patch("inference.torch.topk") as mock_topk:
                    # Setup mock return values
                    mock_probs = MagicMock()
                    mock_probs.shape = [1] # Batch size 1
                    mock_softmax.return_value.squeeze.return_value = mock_probs
                    
                    # topk returns values, indices
                    mock_values = MagicMock()
                    mock_values.tolist.return_value = [0.95]
                    mock_indices = MagicMock()
                    mock_indices.tolist.return_value = [0]
                    
                    mock_topk.return_value = (mock_values, mock_indices)
                    
                    result = predict(b"fake_image_data")
                    
                    assert "top1" in result
                    assert result["top1"][0]["label"] == "ramen"
                    assert result["top1"][0]["score"] == 0.95

def test_predict_error():
    """Test prediction error handling"""
    # If image open fails
    with patch("inference.Image.open", side_effect=Exception("Invalid image")):
        with pytest.raises(Exception):
            predict(b"bad_data")
