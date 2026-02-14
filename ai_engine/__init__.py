"""
DevOS AI Engine
AI-powered command interpretation and generation
"""

__version__ = "0.1.0"
__author__ = "DevOS Team"

from ai_engine.core.processor import AIProcessor, ExecutionResult
from ai_engine.adapters.llm_adapter import (
    LLMAdapter,
    OllamaAdapter,
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    get_adapter
)
from ai_engine.security.validator import SecurityValidator, RiskLevel
from ai_engine.memory.store import MemoryStore
from ai_engine.plugins.plugin_manager import PluginInterface, PluginManager

__all__ = [
    'AIProcessor',
    'ExecutionResult',
    'LLMAdapter',
    'OllamaAdapter',
    'OpenAIAdapter',
    'AnthropicAdapter',
    'GeminiAdapter',
    'get_adapter',
    'SecurityValidator',
    'RiskLevel',
    'MemoryStore',
    'PluginInterface',
    'PluginManager',
]
