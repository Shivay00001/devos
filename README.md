# DevOS - AI-Native Developer Operating Layer

<div align="center">

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗ ███████╗██╗   ██╗ ██████╗ ███████╗           ║
║   ██╔══██╗██╔════╝██║   ██║██╔═══██╗██╔════╝           ║
║   ██║  ██║█████╗  ██║   ██║██║   ██║███████╗           ║
║   ██║  ██║██╔══╝  ╚██╗ ██╔╝██║   ██║╚════██║           ║
║   ██████╔╝███████╗ ╚████╔╝ ╚██████╔╝███████║           ║
║   ╚═════╝ ╚══════╝  ╚═══╝   ╚═════╝ ╚══════╝           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

**Cross-Platform AI-Native Developer Orchestration Layer**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Go 1.21+](https://img.shields.io/badge/go-1.21+-00ADD8.svg)](https://golang.org/)

</div>

## 🌟 What is DevOS?

DevOS is **NOT a kernel** - it's a system-level intelligent orchestration layer that sits on top of your existing OS. Think of it as an AI-powered command center that understands natural language and translates your intentions into safe, validated system operations.

### Key Features

- 🧠 **Natural Language Interface**: Describe what you want, not how to do it
- 🔒 **Security First**: Built-in command validation and sandboxing
- 🌐 **Cross-Platform**: Runs on Windows, macOS, and Linux
- 🤖 **Multi-LLM Support**: OpenAI, Anthropic Claude, Google Gemini, or local Ollama
- 🔌 **Plugin System**: Extensible architecture for custom functionality
- 💾 **Context Memory**: SQLite-based persistent memory across sessions
- 📊 **Project Scaffolding**: Intelligent project setup and management
- 🔍 **Error Analysis**: Automatic error detection and fixing suggestions

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (required)
- **Go 1.21+** (optional, for CLI)
- **Ollama** (optional, for local LLM)

### Installation

#### Unix/Linux/macOS

```bash
git clone https://github.com/devos-ai/devos.git
cd devos
chmod +x installer/install.sh
./installer/install.sh
```

#### Windows

```powershell
git clone https://github.com/devos-ai/devos.git
cd devos
PowerShell -ExecutionPolicy Bypass -File installer\install.ps1
```

#### Via pip (Python only)

```bash
pip install devos-ai
```

## 📖 Usage

### Interactive Mode

```bash
devos
```

### Example Commands

```bash
# Project Setup
devos> setup fastapi project with docker
devos> create react app with typescript

# System Analysis
devos> analyze system performance
devos> check disk usage

# Debugging
devos> fix build error in current directory
devos> analyze error logs

# Git Operations
devos> commit changes with smart message
devos> safe push to origin

# Package Management
devos> install dependencies from requirements.txt
devos> update all npm packages
```

## 🏗️ Architecture

```
devos/
├── core-cli/              # Go-based CLI control engine
│   ├── main.go           # Entry point
│   └── internal/
│       ├── config/       # Configuration management
│       ├── executor/     # Command execution
│       └── logger/       # Structured logging
│
├── ai-engine/            # Python-based AI reasoning core
│   ├── core/
│   │   └── processor.py  # Natural language processing
│   ├── adapters/
│   │   └── llm_adapter.py # Multi-LLM support
│   ├── security/
│   │   └── validator.py  # Command validation
│   └── plugins/
│       └── plugin_manager.py # Plugin system
│
├── adapters/             # OS-specific adapters
│   ├── windows/
│   ├── macos/
│   └── linux/
│
├── memory/               # Context persistence
│   └── store.py         # SQLite memory store
│
└── plugins/              # Plugin ecosystem
    └── community/
        └── git-helper/   # Example plugin
```

## 🔧 Configuration

DevOS stores configuration in platform-specific locations:

- **Windows**: `%APPDATA%\devos\config.json`
- **macOS**: `~/Library/Application Support/devos/config.json`
- **Linux**: `~/.config/devos/config.json`

### Example Configuration

```json
{
  "ai_provider": "ollama",
  "model": "llama3.2",
  "confirmation_mode": true,
  "sandbox_mode": true,
  "log_level": "info"
}
```

### Supported AI Providers

1. **Ollama** (Local, Free)
   ```json
   {
     "ai_provider": "ollama",
     "model": "llama3.2",
     "base_url": "http://localhost:11434"
   }
   ```

2. **OpenAI**
   ```json
   {
     "ai_provider": "openai",
     "model": "gpt-4",
     "api_key": "your-api-key"
   }
   ```

3. **Anthropic Claude**
   ```json
   {
     "ai_provider": "anthropic",
     "model": "claude-3-5-sonnet-20241022",
     "api_key": "your-api-key"
   }
   ```

4. **Google Gemini**
   ```json
   {
     "ai_provider": "gemini",
     "model": "gemini-pro",
     "api_key": "your-api-key"
   }
   ```

## 🔒 Security Features

### Command Validation

DevOS validates all commands before execution:

- ✅ Blocked dangerous commands (rm -rf /, format, etc.)
- ✅ Risk level assessment
- ✅ Confirmation for destructive operations
- ✅ Sandbox execution environment

### Blocked Patterns

```python
BLOCKED_COMMANDS = [
    r'rm\s+-rf\s+/',
    r'mkfs',
    r'dd\s+if=.*of=/dev/',
    r'format\s+[a-zA-Z]:',
    r':\(\)\{:\|:&\};:',  # Fork bomb
]
```

## 🔌 Plugin System

### Creating a Plugin

1. **Create plugin directory**:
   ```
   ~/.config/devos/plugins/my-plugin/
   ├── manifest.json
   └── plugin.py
   ```

2. **Define manifest.json**:
   ```json
   {
     "name": "my-plugin",
     "version": "0.1.0",
     "description": "My awesome plugin",
     "entry_point": "plugin.py",
     "permissions": ["execute_commands"]
   }
   ```

3. **Implement plugin.py**:
   ```python
   from plugins.plugin_manager import PluginInterface
   
   class Plugin(PluginInterface):
       @property
       def name(self) -> str:
           return "my-plugin"
       
       def execute(self, context):
           # Plugin logic here
           return {'success': True, 'output': 'Done!'}
   ```

## 📊 Memory & Context

DevOS maintains context across sessions using SQLite:

- Command history
- Project context
- User preferences
- Execution results

### Example Context Operations

```python
from memory.store import MemoryStore

store = MemoryStore()

# Store context
store.set_context('current_project', '/path/to/project')

# Retrieve context
project = store.get_context('current_project')

# Search history
results = store.search_history('docker')
```

## 🎯 Use Cases

### 1. Project Scaffolding

```bash
devos> setup fastapi project with docker, postgres, and redis
```

Creates:
- Project structure
- Dockerfile & docker-compose.yml
- Requirements.txt
- Main application file
- Configuration files

### 2. Debugging Assistant

```bash
devos> fix build error
```

Analyzes:
- Build logs
- Error messages
- Stack traces
- Suggests fixes

### 3. System Monitoring

```bash
devos> analyze system performance
```

Reports:
- CPU usage
- Memory consumption
- Disk space
- Network activity

### 4. Dependency Management

```bash
devos> install python dependencies from requirements.txt
```

Handles:
- Package manager detection
- Dependency resolution
- Virtual environment setup
- Version conflicts

## 🛠️ Development

### Building from Source

#### Go CLI

```bash
cd core-cli
go mod download
go build -o devos .
```

#### Python Engine

```bash
pip install -e .
```

### Running Tests

```bash
# Python tests
pytest tests/

# Go tests
cd core-cli
go test ./...
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- 🔌 New plugins
- 🌐 Additional LLM adapters
- 🎨 UI improvements
- 📚 Documentation
- 🐛 Bug fixes

## 🚨 Important Notes

### This is NOT:

- ❌ A kernel or OS replacement
- ❌ A fully autonomous agent
- ❌ Production-ready without testing
- ❌ A substitute for understanding commands

### This IS:

- ✅ An intelligent orchestration layer
- ✅ A developer productivity tool
- ✅ A learning and experimentation platform
- ✅ Extensible and customizable

### ⚠️ Reality Check

> **"Agar tum sirf prompt deke expect kar rahe ho: 'Agent sab bana dega perfect production system' Toh nahi hoga."**

You must:
- Understand the architecture
- Audit the code
- Test security features
- Iterate and improve

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by:
- Docker's container orchestration
- Kubernetes' declarative configuration
- PowerShell's pipeline architecture
- Ollama's local-first approach

## 📞 Support

- 📖 [Documentation](https://docs.devos.ai)
- 💬 [GitHub Discussions](https://github.com/devos-ai/devos/discussions)
- 🐛 [Issue Tracker](https://github.com/devos-ai/devos/issues)
- 🌟 [Discord Community](https://discord.gg/devos)

---

<div align="center">

**Built with ❤️ by developers, for developers**

[Website](https://devos.ai) • [Documentation](https://docs.devos.ai) • [GitHub](https://github.com/devos-ai/devos)

</div>
