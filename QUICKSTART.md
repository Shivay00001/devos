# DevOS Quick Start Guide

Get DevOS running in 5 minutes!

## Prerequisites Check

Before installing, verify you have:

```bash
# Check Python (required)
python3 --version
# Should be 3.8 or higher

# Check Go (optional, for CLI)
go version
# Should be 1.21 or higher

# Check Ollama (optional, for local AI)
ollama --version
```

## Installation

### Option 1: Automated Installer (Recommended)

**Linux/macOS:**
```bash
git clone https://github.com/devos-ai/devos.git
cd devos
chmod +x installer/install.sh
./installer/install.sh
```

**Windows:**
```powershell
git clone https://github.com/devos-ai/devos.git
cd devos
PowerShell -ExecutionPolicy Bypass -File installer\install.ps1
```

### Option 2: pip Install (Python Only)

```bash
pip install devos-ai
```

## First Run

### 1. Start DevOS

```bash
devos
```

You should see:
```
╔══════════════════════════════════════════════════════════╗
║   ██████╗ ███████╗██╗   ██╗ ██████╗ ███████╗           ║
║   ██╔══██╗██╔════╝██║   ██║██╔═══██╗██╔════╝           ║
║   ██║  ██║█████╗  ██║   ██║██║   ██║███████╗           ║
║   ██║  ██║██╔══╝  ╚██╗ ██╔╝██║   ██║╚════██║           ║
║   ██████╔╝███████╗ ╚████╔╝ ╚██████╔╝███████║           ║
╚══════════════════════════════════════════════════════════╝

🚀 DevOS is ready. Type 'help' for commands or use natural language.

devos>
```

### 2. Try Your First Commands

```bash
# Check system status
devos> status

# Get help
devos> help

# List directory
devos> show files in current directory
```

## Configuration

### Set Your AI Provider

**Option A: Use Ollama (Local, Free)**

1. Install Ollama:
   ```bash
   # Visit https://ollama.ai and install
   ollama pull llama3.2
   ```

2. DevOS will use Ollama by default!

**Option B: Use Cloud AI (OpenAI/Anthropic/Gemini)**

Edit config file:
- Linux: `~/.config/devos/config.json`
- macOS: `~/Library/Application Support/devos/config.json`
- Windows: `%APPDATA%\devos\config.json`

```json
{
  "ai_provider": "openai",
  "model": "gpt-4",
  "api_key": "your-api-key-here"
}
```

## Example Workflows

### 1. Create a FastAPI Project

```bash
devos> setup fastapi project with docker
```

This creates:
```
my-fastapi-app/
├── main.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### 2. Analyze System Performance

```bash
devos> analyze system performance
```

Output:
```
CPU Usage: 23.4%
Memory: 8.2GB / 16GB (51.25%)
Disk: 145GB / 500GB (29%)
```

### 3. Git Operations

```bash
devos> commit changes with meaningful message
devos> push to remote
```

### 4. Fix Errors

```bash
devos> fix build error
```

DevOS will:
1. Scan logs
2. Identify the issue
3. Suggest fixes
4. Execute with your approval

## Common Commands

```bash
# System
devos> check disk space
devos> show running processes
devos> analyze memory usage

# Development
devos> create react app
devos> install dependencies
devos> run tests

# Git
devos> git status
devos> create new branch
devos> merge branch

# Docker
devos> start containers
devos> show logs
devos> rebuild image
```

## Tips

### 1. Be Specific

❌ `devos> setup project`
✅ `devos> setup fastapi project with postgres and docker`

### 2. Use Confirmation Mode

Keep it enabled for safety:
```json
"confirmation_mode": true
```

### 3. Review Commands

Always check what DevOS will execute before approving.

### 4. Check Logs

If something goes wrong:
```bash
# Linux/macOS
tail -f ~/.local/share/devos/logs/devos-*.log

# Windows
Get-Content $env:APPDATA\devos\logs\devos-*.log -Wait
```

## Troubleshooting

### DevOS Won't Start

```bash
# Check Python
python3 --version

# Check installation
pip show devos-ai

# Reinstall
pip install --force-reinstall devos-ai
```

### Ollama Connection Error

```bash
# Start Ollama server
ollama serve

# Test connection
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "test"
}'
```

### Command Not Found After Install

```bash
# Restart terminal or:
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS
# Restart PowerShell (Windows)
```

### Permission Errors

```bash
# Linux/macOS: Check file permissions
ls -la ~/.config/devos/

# Windows: Run as Administrator if needed
```

## Next Steps

1. **Read Documentation**
   - [Examples](docs/EXAMPLES.md)
   - [Security Guide](docs/SECURITY.md)
   - [Architecture](docs/ARCHITECTURE.md)

2. **Try Advanced Features**
   - Create custom plugins
   - Set up project templates
   - Configure security rules

3. **Join Community**
   - GitHub Discussions
   - Discord Server
   - Report bugs/features

## Getting Help

- 📖 Docs: https://docs.devos.ai
- 💬 Discord: https://discord.gg/devos
- 🐛 Issues: https://github.com/devos-ai/devos/issues
- 📧 Email: support@devos.ai

## Security Note

⚠️ **Important:** DevOS executes system commands. Always:
- Review commands before approving
- Keep confirmation mode enabled
- Understand what each command does
- Don't blindly trust AI output

## Uninstalling

If you need to remove DevOS:

```bash
# Remove Python package
pip uninstall devos-ai

# Remove config files (optional)
# Linux
rm -rf ~/.config/devos

# macOS
rm -rf ~/Library/Application\ Support/devos

# Windows
Remove-Item -Recurse $env:APPDATA\devos
```

---

**You're ready to go! Start with simple commands and gradually explore more features.**

```bash
devos> Let's build something amazing!
```
