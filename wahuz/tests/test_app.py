import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import MLOpsApp

class TestMLOpsApp:
    
    @pytest.fixture
    def app(self):
        """Create MLOpsApp instance for testing"""
        with patch('app.KafkaProducer'):
            return MLOpsApp()
    
    def test_chunk_text(self, app):
        """Test text chunking functionality"""
        text = "This is a test text that should be chunked into smaller pieces for processing."
        chunks = app.chunk_text(text, chunk_size=20, overlap=5)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 25 for chunk in chunks)  # 20 + 5 overlap
        
    def test_chunk_text_small_text(self, app):
        """Test chunking with text smaller than chunk size"""
        text = "Small text"
        chunks = app.chunk_text(text, chunk_size=100, overlap=10)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    @patch('app.PyPDF2.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader, app):
        """Test PDF text extraction"""
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_reader = Mock()
        mock_reader.pages = [mock_page, mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        pdf_bytes = b"fake pdf content"
        result = app.extract_text_from_pdf(pdf_bytes)
        
        assert result == "Test PDF contentTest PDF content"
        mock_pdf_reader.assert_called_once()
    
    @patch('app.genai.embed_content')
    def test_build_index(self, mock_embed, app):
        """Test embedding index building"""
        # Mock embedding response
        mock_embed.return_value = {"embedding": [0.1, 0.2, 0.3, 0.4]}
        
        chunks = ["chunk1", "chunk2", "chunk3"]
        embeddings = app.build_index(chunks)
        
        assert embeddings.shape == (3, 4)
        assert mock_embed.call_count == 3
        
        # Check normalization
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_allclose(norms, 1.0, rtol=1e-10)
    
    @patch('app.genai.embed_content')
    def test_retrieve(self, mock_embed, app):
        """Test chunk retrieval"""
        # Mock query embedding
        mock_embed.return_value = {"embedding": [1.0, 0.0, 0.0]}
        
        chunks = ["relevant chunk", "less relevant", "not relevant"]
        embeddings = np.array([
            [1.0, 0.0, 0.0],  # Perfect match
            [0.5, 0.5, 0.0],  # Partial match
            [0.0, 1.0, 0.0]   # No match
        ])
        
        result = app.retrieve("test query", chunks, embeddings, top_k=2)
        
        assert len(result) == 2
        assert result[0] == "relevant chunk"
    
    @patch('app.genai.GenerativeModel')
    def test_ask_gemini(self, mock_model_class, app):
        """Test Gemini answer generation"""
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "This is the generated answer"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        context = "Some context"
        question = "What is this about?"
        
        result = app.ask_gemini(context, question)
        
        assert result == "This is the generated answer"
        mock_model.generate_content.assert_called_once()
    
    def test_send_event_no_kafka(self, app):
        """Test event sending when Kafka is not available"""
        app.kafka_producer = None
        
        # Should not raise exception
        app.send_event("test_topic", {"test": "data"})
    
    @patch('app.KafkaProducer')
    def test_send_event_with_kafka(self, mock_kafka_producer):
        """Test event sending with Kafka"""
        mock_producer = Mock()
        mock_kafka_producer.return_value = mock_producer
        
        app = MLOpsApp()
        app.send_event("test_topic", {"test": "data"})
        
        mock_producer.send.assert_called_once_with("test_topic", {"test": "data"})

if __name__ == "__main__":
    pytest.main([__file__])
