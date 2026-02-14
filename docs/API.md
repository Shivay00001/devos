# DevOS API Documentation

## Table of Contents
1. [Core API](#core-api)
2. [Security API](#security-api)
3. [Memory API](#memory-api)
4. [LLM Adapters API](#llm-adapters-api)
5. [Plugin API](#plugin-api)

---

## Core API

### AIProcessor

The main entry point for processing natural language commands.

#### Constructor

```python
AIProcessor(config: Dict[str, Any])
```

**Parameters:**
- `config` (dict): Configuration dictionary
  - `os` (str): Operating system ('linux', 'windows', 'darwin')
  - `provider` (str): LLM provider ('ollama', 'openai', 'anthropic', 'gemini')
  - `model` (str): Model name
  - `api_key` (str, optional): API key for cloud providers
  - `base_url` (str, optional): Custom base URL for Ollama

#### Methods

##### process(user_input: str) -> ExecutionResult

Process natural language input and generate commands.

**Parameters:**
- `user_input` (str): Natural language command from user

**Returns:**
- `ExecutionResult`: Object containing:
  - `output` (str): Human-readable description
  - `commands` (List[str]): List of generated commands
  - `needs_confirmation` (bool): Whether confirmation is needed
  - `error` (str): Error message if processing failed

**Example:**
```python
from ai_engine import AIProcessor

processor = AIProcessor({
    'os': 'linux',
    'provider': 'ollama',
    'model': 'llama3.2'
})

result = processor.process('setup fastapi project')
print(result.output)
print(result.commands)
# Output: ['mkdir -p "my-fastapi-app"', 'touch "my-fastapi-app/main.py"', ...]
```

**Rate Limiting:**
- Maximum 100 calls per 60 seconds
- Exceeding limit raises Exception

**Input Validation:**
- Maximum 10,000 characters
- Blocks XSS patterns (script tags, javascript: URLs)
- Blocks HTML event handlers

---

## Security API

### SecurityValidator

Validates commands for security risks.

#### Constructor

```python
SecurityValidator()
```

#### Methods

##### validate_command(command: str) -> Tuple[bool, RiskLevel, str]

Validate a single command.

**Parameters:**
- `command` (str): Command to validate

**Returns:**
- Tuple of:
  - `is_allowed` (bool): Whether command is allowed
  - `risk_level` (RiskLevel): Risk level enum
  - `reason` (str): Explanation of validation result

**Risk Levels:**
- `RiskLevel.SAFE` (1): No risk
- `RiskLevel.LOW` (2): Minimal risk
- `RiskLevel.MEDIUM` (3): Requires awareness (e.g., sudo)
- `RiskLevel.HIGH` (4): Requires confirmation (e.g., rm -rf)
- `RiskLevel.CRITICAL` (5): Blocked (e.g., rm -rf /, fork bomb)

**Example:**
```python
from ai_engine import SecurityValidator, RiskLevel

validator = SecurityValidator()

# Safe command
allowed, level, reason = validator.validate_command('ls -la')
# allowed=True, level=RiskLevel.SAFE, reason="Command appears safe"

# Dangerous command
allowed, level, reason = validator.validate_command('rm -rf /')
# allowed=False, level=RiskLevel.CRITICAL, reason="Blocked command..."
```

##### validate_commands(commands: List[str]) -> Dict[str, Any]

Validate multiple commands.

**Returns:**
- Dictionary with:
  - `all_allowed` (bool): Whether all commands are allowed
  - `needs_confirmation` (bool): Whether any command needs confirmation
  - `max_risk_level` (RiskLevel): Highest risk level
  - `blocked` (List[str]): Blocked commands
  - `warnings` (List[str]): Warning messages
  - `details` (List[Dict]): Per-command details

##### sanitize_command(command: str) -> str

Sanitize command by removing dangerous elements.

**Example:**
```python
sanitized = validator.sanitize_command('ls -la # comment')
# Returns: 'ls -la'
```

### CommandSandbox

Provides sandboxed command execution environment.

#### Constructor

```python
CommandSandbox(work_dir: str = None)
```

#### Methods

##### can_execute(command: str) -> Tuple[bool, str]

Check if command can execute in sandbox.

**Returns:**
- Tuple of:
  - `can_execute` (bool): Whether execution is allowed
  - `reason` (str): Explanation

##### prepare_environment() -> Dict[str, str]

Prepare sandboxed environment variables.

**Returns:**
- Dictionary of environment variables with restricted PATH

---

## Memory API

### MemoryStore

SQLite-based context and command history store.

#### Constructor

```python
MemoryStore(db_path: str = None)
```

**Parameters:**
- `db_path` (str, optional): Path to SQLite database. If None, uses default location.

#### Methods

##### add_command(user_input: str, intent: str, commands: List[str], success: bool, output: str = "", error: str = "", metadata: Dict = None) -> int

Add command execution to history.

**Returns:**
- `record_id` (int): ID of inserted record

**Example:**
```python
from ai_engine import MemoryStore

store = MemoryStore()
record_id = store.add_command(
    user_input='setup fastapi project',
    intent='project_setup',
    commands=['mkdir myapp', 'cd myapp'],
    success=True
)
```

##### get_recent_commands(limit: int = 10) -> List[Dict[str, Any]]

Get recent command history.

**Returns:**
- List of command records with fields:
  - `id`, `timestamp`, `user_input`, `intent`
  - `commands`, `success`, `output`, `error`

##### search_history(query: str, limit: int = 20) -> List[Dict[str, Any]]

Search command history.

**Example:**
```python
results = store.search_history('fastapi')
# Returns commands containing 'fastapi'
```

##### set_context(key: str, value: Any, category: str = "general", metadata: Dict = None)

Store context value.

**Example:**
```python
store.set_context('current_project', '/path/to/project')
store.set_context('preferred_editor', 'vscode', category='preferences')
```

##### get_context(key: str) -> Optional[Any]

Get context value.

**Returns:**
- Context value or None if not found

##### get_context_by_category(category: str) -> Dict[str, Any]

Get all context values in a category.

**Example:**
```python
prefs = store.get_context_by_category('preferences')
# Returns: {'preferred_editor': 'vscode', ...}
```

##### save_project_context(project_path: str, project_type: str, dependencies: List[str], metadata: Dict = None)

Save project context.

**Example:**
```python
store.save_project_context(
    project_path='/home/user/myproject',
    project_type='fastapi',
    dependencies=['fastapi', 'uvicorn', 'pydantic']
)
```

##### get_project_context(project_path: str) -> Optional[Dict[str, Any]]

Get project context.

##### cleanup_old_records(days: int = 30)

Clean up records older than specified days.

---

## LLM Adapters API

### Factory Function

```python
get_adapter(provider: str, model: str, api_key: str = None, base_url: str = None) -> LLMAdapter
```

**Supported Providers:**
- `'ollama'` - Local Ollama instance
- `'openai'` - OpenAI API
- `'anthropic'` - Anthropic Claude API
- `'gemini'` - Google Gemini API

### OllamaAdapter

```python
OllamaAdapter(model: str = "llama3.2", base_url: str = "http://localhost:11434")
```

#### Methods

##### generate(prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str

Generate response using Ollama.

**Example:**
```python
from ai_engine import get_adapter

adapter = get_adapter('ollama', 'llama3.2')
response = adapter.generate("Generate a bash command to list files")
```

### OpenAIAdapter

```python
OpenAIAdapter(model: str = "gpt-4", api_key: str = None)
```

Uses `OPENAI_API_KEY` environment variable if api_key not provided.

### AnthropicAdapter

```python
AnthropicAdapter(model: str = "claude-3-5-sonnet-20241022", api_key: str = None)
```

Uses `ANTHROPIC_API_KEY` environment variable if api_key not provided.

### GeminiAdapter

```python
GeminiAdapter(model: str = "gemini-pro", api_key: str = None)
```

Uses `GOOGLE_API_KEY` environment variable if api_key not provided.

---

## Plugin API

### PluginInterface

Abstract base class for plugins.

```python
from ai_engine import PluginInterface

class MyPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "My plugin description"
    
    def initialize(self, config: Dict):
        # Initialize plugin
        pass
    
    def execute(self, context: Dict) -> Dict:
        # Execute plugin logic
        return {'success': True, 'output': 'Done'}
    
    def get_commands(self) -> List[str]:
        return ['mycommand', 'myplugin']
```

### PluginManager

```python
from ai_engine import PluginManager

manager = PluginManager(plugin_dir='/path/to/plugins')

# Discover plugins
plugins = manager.discover_plugins()

# Load plugin
manager.load_plugin('my-plugin')

# Execute plugin
result = manager.execute_plugin('my-plugin', {'command': 'test'})

# List loaded plugins
loaded = manager.list_plugins()
```

---

## Error Handling

All APIs use exceptions for error handling:

- `ValueError`: Invalid input or configuration
- `Exception`: General errors with descriptive messages

**Example:**
```python
from ai_engine import AIProcessor

processor = AIProcessor({'os': 'linux'})

try:
    result = processor.process('<script>alert(1)</script>')
except ValueError as e:
    print(f"Invalid input: {e}")
```

---

## Configuration

### Default Configuration

```json
{
  "os": "linux",
  "ai_provider": "ollama",
  "model": "llama3.2",
  "confirmation_mode": true,
  "log_level": "info",
  "max_tokens": 2048,
  "temperature": 0.7,
  "sandbox_mode": true,
  "blocked_commands": [
    "rm -rf /",
    "dd if=",
    "mkfs",
    "format",
    ":(){:|:&};:"
  ],
  "memory_size": 100
}
```

---

## Best Practices

1. **Always validate commands** before execution:
```python
validator = SecurityValidator()
allowed, level, reason = validator.validate_command(cmd)
if not allowed:
    raise Exception(f"Command blocked: {reason}")
```

2. **Use context managers for resources**:
```python
with tempfile.TemporaryDirectory() as tmpdir:
    store = MemoryStore(os.path.join(tmpdir, 'memory.db'))
    # Use store...
```

3. **Handle rate limits gracefully**:
```python
try:
    result = processor.process(user_input)
except Exception as e:
    if "Rate limit" in str(e):
        time.sleep(1)
        result = processor.process(user_input)
```

4. **Store context for better UX**:
```python
store.set_context('last_project', current_project)
# Later...
last_project = store.get_context('last_project')
```

---

## Type Hints

All APIs support Python type hints:

```python
from typing import Dict, List, Any
from ai_engine import AIProcessor, ExecutionResult

def process_command(processor: AIProcessor, input: str) -> ExecutionResult:
    return processor.process(input)
```

---

For more examples and advanced usage, see the `examples/` directory and test files.
