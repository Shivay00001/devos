"""
Tests for AI Engine Processor
"""

import pytest
import json
from ai_engine.core.processor import AIProcessor, ExecutionResult


class TestAIProcessor:
    """Test cases for AIProcessor"""
    
    @pytest.fixture
    def processor(self):
        config = {
            'provider': 'ollama',
            'model': 'llama3.2',
            'os': 'linux'
        }
        return AIProcessor(config)
    
    def test_initialization(self, processor):
        """Test processor initialization"""
        assert processor.provider == 'ollama'
        assert processor.model == 'llama3.2'
        assert processor.os == 'linux'
    
    def test_process_valid_input(self, processor):
        """Test processing valid input"""
        result = processor.process("setup fastapi project")
        assert isinstance(result, ExecutionResult)
        assert result.output is not None
        assert isinstance(result.commands, list)
        assert isinstance(result.needs_confirmation, bool)
    
    def test_process_empty_input(self, processor):
        """Test processing empty input"""
        with pytest.raises(ValueError, match="Invalid input"):
            processor.process("")
    
    def test_process_none_input(self, processor):
        """Test processing None input"""
        with pytest.raises(ValueError, match="Invalid input"):
            processor.process(None)
    
    def test_process_long_input(self, processor):
        """Test processing too long input"""
        long_input = "x" * 10001
        with pytest.raises(ValueError, match="Input too long"):
            processor.process(long_input)
    
    def test_contains_dangerous_patterns_script(self, processor):
        """Test detection of script tags"""
        assert processor._contains_dangerous_patterns('<script>alert(1)</script>')
    
    def test_contains_dangerous_patterns_javascript(self, processor):
        """Test detection of javascript: protocol"""
        assert processor._contains_dangerous_patterns('javascript:alert(1)')
    
    def test_contains_dangerous_patterns_clean(self, processor):
        """Test that clean input passes"""
        assert not processor._contains_dangerous_patterns('setup fastapi project')
    
    def test_classify_intent_project_setup(self, processor):
        """Test intent classification for project setup"""
        intent = processor._classify_intent('setup fastapi project')
        assert intent == 'project_setup'
    
    def test_classify_intent_debug(self, processor):
        """Test intent classification for debug"""
        intent = processor._classify_intent('fix build error')
        assert intent == 'debug'
    
    def test_classify_intent_analyze(self, processor):
        """Test intent classification for analyze"""
        intent = processor._classify_intent('analyze system performance')
        assert intent == 'analyze'
    
    def test_classify_intent_install(self, processor):
        """Test intent classification for install"""
        intent = processor._classify_intent('install dependencies')
        assert intent == 'install'
    
    def test_classify_intent_general(self, processor):
        """Test intent classification for general queries"""
        intent = processor._classify_intent('hello world')
        assert intent == 'general'
    
    def test_plan_project_setup_fastapi(self, processor):
        """Test project setup planning for FastAPI"""
        plan = processor._generate_plan('setup fastapi project', 'project_setup')
        assert plan['intent'] == 'project_setup'
        assert len(plan['steps']) > 0
        assert 'description' in plan
    
    def test_plan_debug(self, processor):
        """Test debug planning"""
        plan = processor._generate_plan('fix error', 'debug')
        assert plan['intent'] == 'debug'
        assert len(plan['steps']) > 0
    
    def test_plan_analyze(self, processor):
        """Test analyze planning"""
        plan = processor._generate_plan('analyze performance', 'analyze')
        assert plan['intent'] == 'analyze'
        assert len(plan['steps']) > 0
    
    def test_cmd_mkdir_linux(self, processor):
        """Test mkdir command for Linux"""
        processor.os = 'linux'
        cmd = processor._cmd_mkdir('test-dir')
        assert 'mkdir -p' in cmd
        assert 'test-dir' in cmd
    
    def test_cmd_mkdir_windows(self, processor):
        """Test mkdir command for Windows"""
        processor.os = 'windows'
        cmd = processor._cmd_mkdir('test-dir')
        assert 'New-Item' in cmd
        assert 'test-dir' in cmd
    
    def test_cmd_cpu_usage_linux(self, processor):
        """Test CPU usage command for Linux"""
        processor.os = 'linux'
        cmd = processor._cmd_cpu_usage()
        assert 'top' in cmd
    
    def test_cmd_cpu_usage_windows(self, processor):
        """Test CPU usage command for Windows"""
        processor.os = 'windows'
        cmd = processor._cmd_cpu_usage()
        assert 'Win32_Processor' in cmd
    
    def test_cmd_cpu_usage_darwin(self, processor):
        """Test CPU usage command for macOS"""
        processor.os = 'darwin'
        cmd = processor._cmd_cpu_usage()
        assert 'top' in cmd
    
    def test_needs_confirmation_with_dangerous(self, processor):
        """Test confirmation detection for dangerous commands"""
        commands = ['rm -rf /tmp/test', 'ls -la']
        assert processor._needs_confirmation(commands)
    
    def test_needs_confirmation_safe(self, processor):
        """Test confirmation detection for safe commands"""
        commands = ['ls -la', 'pwd']
        assert not processor._needs_confirmation(commands)
    
    def test_format_output(self, processor):
        """Test output formatting"""
        plan = {
            'description': 'Test plan',
            'steps': [
                {'action': 'test_action'},
                {'action': 'another_action'}
            ]
        }
        commands = ['cmd1', 'cmd2']
        output = processor._format_output(plan, commands)
        
        assert 'Test plan' in output
        assert 'Test Action' in output
        assert 'Another Action' in output


class TestExecutionResult:
    """Test cases for ExecutionResult dataclass"""
    
    def test_execution_result_creation(self):
        """Test ExecutionResult creation"""
        result = ExecutionResult(
            output='test output',
            commands=['cmd1', 'cmd2'],
            needs_confirmation=True,
            error=''
        )
        assert result.output == 'test output'
        assert result.commands == ['cmd1', 'cmd2']
        assert result.needs_confirmation is True
        assert result.error == ''
    
    def test_execution_result_defaults(self):
        """Test ExecutionResult defaults"""
        result = ExecutionResult(
            output='test',
            commands=[],
            needs_confirmation=False
        )
        assert result.error == ''


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
