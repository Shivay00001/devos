"""
Tests for LLM Adapters
"""

import pytest
from unittest.mock import patch, Mock
from ai_engine.adapters.llm_adapter import (
    OllamaAdapter,
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    get_adapter
)


class TestOllamaAdapter:
    """Test cases for OllamaAdapter"""
    
    @pytest.fixture
    def adapter(self):
        return OllamaAdapter(model="llama3.2")
    
    def test_initialization(self, adapter):
        """Test adapter initialization"""
        assert adapter.model == "llama3.2"
        assert adapter.base_url == "http://localhost:11434"
    
    def test_initialization_custom_url(self):
        """Test adapter with custom URL"""
        adapter = OllamaAdapter(model="test", base_url="http://custom:11434")
        assert adapter.base_url == "http://custom:11434"
    
    @patch('requests.post')
    def test_generate_success(self, mock_post, adapter):
        """Test successful generation"""
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'Test response'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = adapter.generate("Test prompt")
        assert result == "Test response"
    
    @patch('requests.post')
    def test_generate_connection_error(self, mock_post, adapter):
        """Test connection error handling"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(Exception, match="Cannot connect to Ollama"):
            adapter.generate("Test prompt")


class TestOpenAIAdapter:
    """Test cases for OpenAIAdapter"""
    
    def test_initialization_with_key(self):
        """Test adapter with API key"""
        adapter = OpenAIAdapter(model="gpt-4", api_key="test-key")
        assert adapter.model == "gpt-4"
        assert adapter.api_key == "test-key"
    
    def test_initialization_missing_key(self):
        """Test adapter without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                OpenAIAdapter(model="gpt-4")
    
    def test_initialization_from_env(self):
        """Test adapter reading key from environment"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key'}):
            adapter = OpenAIAdapter(model="gpt-4")
            assert adapter.api_key == "env-key"
    
    @patch('requests.post')
    def test_generate_success(self, mock_post):
        """Test successful generation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        adapter = OpenAIAdapter(model="gpt-4", api_key="test-key")
        result = adapter.generate("Test prompt")
        assert result == "Test response"


class TestAnthropicAdapter:
    """Test cases for AnthropicAdapter"""
    
    def test_initialization_with_key(self):
        """Test adapter with API key"""
        adapter = AnthropicAdapter(model="claude-3", api_key="test-key")
        assert adapter.model == "claude-3"
        assert adapter.api_key == "test-key"
    
    def test_initialization_missing_key(self):
        """Test adapter without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                AnthropicAdapter(model="claude-3")
    
    @patch('requests.post')
    def test_generate_success(self, mock_post):
        """Test successful generation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'content': [{'text': 'Test response'}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        adapter = AnthropicAdapter(model="claude-3", api_key="test-key")
        result = adapter.generate("Test prompt")
        assert result == "Test response"


class TestGeminiAdapter:
    """Test cases for GeminiAdapter"""
    
    def test_initialization_with_key(self):
        """Test adapter with API key"""
        adapter = GeminiAdapter(model="gemini-pro", api_key="test-key")
        assert adapter.model == "gemini-pro"
        assert adapter.api_key == "test-key"
    
    def test_initialization_missing_key(self):
        """Test adapter without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                GeminiAdapter(model="gemini-pro")
    
    @patch('requests.post')
    def test_generate_success(self, mock_post):
        """Test successful generation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'Test response'}]}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        adapter = GeminiAdapter(model="gemini-pro", api_key="test-key")
        result = adapter.generate("Test prompt")
        assert result == "Test response"


class TestGetAdapter:
    """Test cases for get_adapter factory function"""
    
    def test_get_ollama_adapter(self):
        """Test getting Ollama adapter"""
        with patch.dict('os.environ', {}, clear=True):
            adapter = get_adapter('ollama', 'llama3.2')
            assert isinstance(adapter, OllamaAdapter)
    
    def test_get_openai_adapter(self):
        """Test getting OpenAI adapter"""
        adapter = get_adapter('openai', 'gpt-4', api_key='test-key')
        assert isinstance(adapter, OpenAIAdapter)
    
    def test_get_anthropic_adapter(self):
        """Test getting Anthropic adapter"""
        adapter = get_adapter('anthropic', 'claude-3', api_key='test-key')
        assert isinstance(adapter, AnthropicAdapter)
    
    def test_get_gemini_adapter(self):
        """Test getting Gemini adapter"""
        adapter = get_adapter('gemini', 'gemini-pro', api_key='test-key')
        assert isinstance(adapter, GeminiAdapter)
    
    def test_get_adapter_invalid_provider(self):
        """Test getting adapter with invalid provider"""
        with pytest.raises(ValueError, match="Unsupported provider"):
            get_adapter('invalid', 'model')
    
    def test_get_adapter_case_insensitive(self):
        """Test provider name is case insensitive"""
        with patch.dict('os.environ', {}, clear=True):
            adapter = get_adapter('OLLAMA', 'llama3.2')
            assert isinstance(adapter, OllamaAdapter)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
