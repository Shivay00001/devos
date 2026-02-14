"""
DevOS AI Engine - Command Processor
Handles natural language to command translation
"""

import json
import sys
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from functools import wraps
import time


@dataclass
class ExecutionResult:
    """Result of command processing"""
    output: str
    commands: List[str]
    needs_confirmation: bool
    error: str = ""


def rate_limit(max_calls: int = 100, time_window: int = 60):
    """Rate limiting decorator"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get 'self' from args
            self = args[0] if args and hasattr(args[0], '__dict__') else None
            
            if self:
                if not hasattr(self, '_rate_limit_calls'):
                    self._rate_limit_calls = []
                calls_list = self._rate_limit_calls
            else:
                calls_list = calls
                
            now = time.time()
            calls_list[:] = [c for c in calls_list if now - c < time_window]
            
            if len(calls_list) >= max_calls:
                raise Exception(f"Rate limit exceeded. Max {max_calls} calls per {time_window} seconds")
            
            calls_list.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_input(func):
    """Input validation decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args and isinstance(args[0], AIProcessor):
            self = args[0]
            user_input = args[1] if len(args) > 1 else kwargs.get('user_input', '')
            
            if not user_input or not isinstance(user_input, str):
                raise ValueError("Invalid input: must be non-empty string")
            
            if len(user_input) > 10000:
                raise ValueError("Input too long: max 10000 characters")
            
            if self._contains_dangerous_patterns(user_input):
                raise ValueError("Input contains dangerous patterns")
        
        return func(*args, **kwargs)
    return wrapper


class AIProcessor:
    """Main AI processing engine for DevOS"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get('provider', 'ollama')
        self.model = config.get('model', 'llama3.2')
        self.os = config.get('os', 'linux')
        
    def _contains_dangerous_patterns(self, user_input: str) -> bool:
        """Check if input contains dangerous patterns"""
        dangerous_patterns = [
            r'<script[^>]*>.*</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'\\x[0-9a-fA-F]{2}',
            r'%[0-9a-fA-F]{2}',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True
        return False
    
    @validate_input
    @rate_limit(max_calls=100, time_window=60)
    def process(self, user_input: str) -> ExecutionResult:
        """
        Process natural language input and generate commands
        
        Args:
            user_input: Natural language command from user
            
        Returns:
            ExecutionResult with interpreted commands
        """
        try:
            # Classify the intent
            intent = self._classify_intent(user_input)
            
            # Generate execution plan
            plan = self._generate_plan(user_input, intent)
            
            # Convert plan to OS-specific commands
            commands = self._plan_to_commands(plan)
            
            # Determine if confirmation is needed
            needs_confirmation = self._needs_confirmation(commands)
            
            # Generate human-readable output
            output = self._format_output(plan, commands)
            
            return ExecutionResult(
                output=output,
                commands=commands,
                needs_confirmation=needs_confirmation
            )
            
        except Exception as e:
            return ExecutionResult(
                output=f"Failed to process command: {str(e)}",
                commands=[],
                needs_confirmation=False,
                error=str(e)
            )
    
    def _classify_intent(self, user_input: str) -> str:
        """Classify user intent from input"""
        input_lower = user_input.lower()
        
        # Intent classification patterns
        if any(kw in input_lower for kw in ['setup', 'create', 'init', 'scaffold']):
            return 'project_setup'
        elif any(kw in input_lower for kw in ['fix', 'debug', 'error', 'problem']):
            return 'debug'
        elif any(kw in input_lower for kw in ['analyze', 'check', 'inspect', 'performance']):
            return 'analyze'
        elif any(kw in input_lower for kw in ['install', 'add', 'dependency']):
            return 'install'
        elif any(kw in input_lower for kw in ['build', 'compile', 'make']):
            return 'build'
        elif any(kw in input_lower for kw in ['deploy', 'push', 'release']):
            return 'deploy'
        elif any(kw in input_lower for kw in ['test', 'run tests']):
            return 'test'
        else:
            return 'general'
    
    def _generate_plan(self, user_input: str, intent: str) -> Dict[str, Any]:
        """Generate execution plan based on intent"""
        plan = {
            'intent': intent,
            'steps': [],
            'description': ''
        }
        
        if intent == 'project_setup':
            plan['steps'] = self._plan_project_setup(user_input)
            plan['description'] = 'Setting up new project'
        elif intent == 'debug':
            plan['steps'] = self._plan_debug(user_input)
            plan['description'] = 'Analyzing and fixing errors'
        elif intent == 'analyze':
            plan['steps'] = self._plan_analyze(user_input)
            plan['description'] = 'Analyzing system/project'
        elif intent == 'install':
            plan['steps'] = self._plan_install(user_input)
            plan['description'] = 'Installing dependencies'
        else:
            plan['steps'] = self._plan_general(user_input)
            plan['description'] = 'Executing command'
        
        return plan
    
    def _plan_project_setup(self, user_input: str) -> List[Dict[str, str]]:
        """Plan project setup steps"""
        steps = []
        input_lower = user_input.lower()
        
        # Detect project type
        if 'fastapi' in input_lower or 'fast api' in input_lower:
            steps.extend([
                {'action': 'create_directory', 'name': 'my-fastapi-app'},
                {'action': 'create_file', 'path': 'my-fastapi-app/main.py', 
                 'content': 'FastAPI app template'},
                {'action': 'create_file', 'path': 'my-fastapi-app/requirements.txt',
                 'content': 'fastapi\nuvicorn[standard]\npydantic'},
            ])
            
            if 'docker' in input_lower:
                steps.extend([
                    {'action': 'create_file', 'path': 'my-fastapi-app/Dockerfile',
                     'content': 'Dockerfile template'},
                    {'action': 'create_file', 'path': 'my-fastapi-app/docker-compose.yml',
                     'content': 'Docker Compose template'},
                ])
        
        elif 'react' in input_lower:
            steps.append({'action': 'run_command', 'command': 'npx create-react-app my-react-app'})
        
        elif 'django' in input_lower:
            steps.extend([
                {'action': 'run_command', 'command': 'django-admin startproject myproject'},
                {'action': 'create_file', 'path': 'requirements.txt',
                 'content': 'Django>=4.0\ndjango-environ'},
            ])
        
        else:
            # Generic project setup
            steps.append({'action': 'create_directory', 'name': 'my-project'})
        
        return steps
    
    def _plan_debug(self, user_input: str) -> List[Dict[str, str]]:
        """Plan debugging steps"""
        return [
            {'action': 'check_logs', 'path': '.'},
            {'action': 'analyze_errors', 'scope': 'current_directory'},
            {'action': 'suggest_fixes', 'context': user_input},
        ]
    
    def _plan_analyze(self, user_input: str) -> List[Dict[str, str]]:
        """Plan analysis steps"""
        input_lower = user_input.lower()
        
        if 'performance' in input_lower or 'system' in input_lower:
            return [
                {'action': 'check_cpu', 'command': 'cpu_usage'},
                {'action': 'check_memory', 'command': 'memory_usage'},
                {'action': 'check_disk', 'command': 'disk_usage'},
            ]
        else:
            return [
                {'action': 'analyze_directory', 'path': '.'},
            ]
    
    def _plan_install(self, user_input: str) -> List[Dict[str, str]]:
        """Plan installation steps"""
        input_lower = user_input.lower()
        
        if 'requirements.txt' in input_lower or 'python' in input_lower:
            return [{'action': 'run_command', 'command': 'pip install -r requirements.txt'}]
        elif 'package.json' in input_lower or 'npm' in input_lower:
            return [{'action': 'run_command', 'command': 'npm install'}]
        else:
            return [{'action': 'detect_dependencies', 'path': '.'}]
    
    def _plan_general(self, user_input: str) -> List[Dict[str, str]]:
        """Plan general execution"""
        return [{'action': 'execute', 'command': user_input}]
    
    def _plan_to_commands(self, plan: Dict[str, Any]) -> List[str]:
        """Convert execution plan to OS-specific commands"""
        commands = []
        
        for step in plan['steps']:
            action = step.get('action')
            
            if action == 'create_directory':
                commands.append(self._cmd_mkdir(step['name']))
            elif action == 'create_file':
                commands.append(self._cmd_create_file(step['path'], step.get('content', '')))
            elif action == 'run_command':
                commands.append(step['command'])
            elif action == 'check_cpu':
                commands.append(self._cmd_cpu_usage())
            elif action == 'check_memory':
                commands.append(self._cmd_memory_usage())
            elif action == 'check_disk':
                commands.append(self._cmd_disk_usage())
            elif action == 'analyze_directory':
                commands.append(self._cmd_list_directory(step.get('path', '.')))
        
        return commands
    
    def _cmd_mkdir(self, name: str) -> str:
        """OS-specific mkdir command"""
        if self.os == 'windows':
            return f'New-Item -ItemType Directory -Path "{name}"'
        else:
            return f'mkdir -p "{name}"'
    
    def _cmd_create_file(self, path: str, content: str) -> str:
        """OS-specific file creation command"""
        if self.os == 'windows':
            return f'New-Item -ItemType File -Path "{path}" -Force'
        else:
            return f'touch "{path}"'
    
    def _cmd_cpu_usage(self) -> str:
        """OS-specific CPU usage command"""
        if self.os == 'windows':
            return 'Get-WmiObject -Class Win32_Processor | Select-Object LoadPercentage'
        elif self.os == 'darwin':
            return 'top -l 1 | grep "CPU usage"'
        else:
            return 'top -bn1 | grep "Cpu(s)"'
    
    def _cmd_memory_usage(self) -> str:
        """OS-specific memory usage command"""
        if self.os == 'windows':
            return 'Get-WmiObject -Class Win32_OperatingSystem | Select-Object FreePhysicalMemory,TotalVisibleMemorySize'
        elif self.os == 'darwin':
            return 'vm_stat'
        else:
            return 'free -h'
    
    def _cmd_disk_usage(self) -> str:
        """OS-specific disk usage command"""
        if self.os == 'windows':
            return 'Get-PSDrive -PSProvider FileSystem'
        else:
            return 'df -h'
    
    def _cmd_list_directory(self, path: str) -> str:
        """OS-specific directory listing"""
        if self.os == 'windows':
            return f'Get-ChildItem -Path "{path}"'
        else:
            return f'ls -la "{path}"'
    
    def _needs_confirmation(self, commands: List[str]) -> bool:
        """Determine if commands need user confirmation"""
        dangerous_keywords = [
            'rm', 'delete', 'format', 'drop',
            'truncate', 'destroy', 'remove', 'uninstall'
        ]
        
        for cmd in commands:
            cmd_lower = cmd.lower()
            if any(kw in cmd_lower for kw in dangerous_keywords):
                return True
        
        return False
    
    def _format_output(self, plan: Dict[str, Any], commands: List[str]) -> str:
        """Format human-readable output"""
        output = f"[Plan] {plan['description']}\n\n"
        output += f"Steps to execute:\n"
        
        for i, step in enumerate(plan['steps'], 1):
            action = step.get('action', 'unknown')
            output += f"  {i}. {action.replace('_', ' ').title()}\n"
        
        return output.strip()


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'output': 'No input provided',
            'commands': [],
            'needs_confirmation': False,
            'error': 'Missing input argument'
        }))
        sys.exit(1)
    
    try:
        # Parse input JSON
        config = json.loads(sys.argv[1])
        user_input = config.get('input', '')
        
        # Process command
        processor = AIProcessor(config)
        result = processor.process(user_input)
        
        # Output result as JSON
        print(json.dumps(asdict(result)))
        
    except Exception as e:
        print(json.dumps({
            'output': f'Error: {str(e)}',
            'commands': [],
            'needs_confirmation': False,
            'error': str(e)
        }))
        sys.exit(1)


if __name__ == '__main__':
    main()
