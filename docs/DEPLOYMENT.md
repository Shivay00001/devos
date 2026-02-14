# DevOS Deployment Guide

Complete guide for deploying DevOS in production environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Hardening](#security-hardening)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 10GB
- OS: Linux, Windows, or macOS

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+ SSD
- Network: Stable internet connection (for cloud LLMs)

### Software Requirements

**Required:**
- Python 3.8+
- Go 1.21+ (for CLI)

**Optional:**
- Docker 20.10+
- Docker Compose 2.0+
- Ollama (for local LLM)

---

## Installation

### Method 1: Binary Installation (Recommended)

1. **Download the latest release:**
```bash
# Linux
wget https://github.com/devos-ai/devos/releases/latest/download/devos-linux-amd64
chmod +x devos-linux-amd64
sudo mv devos-linux-amd64 /usr/local/bin/devos

# macOS
wget https://github.com/devos-ai/devos/releases/latest/download/devos-darwin-amd64
chmod +x devos-darwin-amd64
sudo mv devos-darwin-amd64 /usr/local/bin/devos

# Windows
# Download devos-windows-amd64.exe from releases page
```

2. **Install Python dependencies:**
```bash
pip install devos-ai
```

3. **Verify installation:**
```bash
devos version
```

### Method 2: Source Installation

1. **Clone the repository:**
```bash
git clone https://github.com/devos-ai/devos.git
cd devos
```

2. **Install Go CLI:**
```bash
cd cmd/devos
go build -o devos .
sudo mv devos /usr/local/bin/
```

3. **Install Python package:**
```bash
cd ../..
pip install -e .
```

### Method 3: Docker Installation

```bash
docker pull devosai/devos:latest
```

---

## Configuration

### Initial Setup

1. **Run DevOS for the first time:**
```bash
devos
```

This creates the default configuration at:
- Linux: `~/.config/devos/config.json`
- macOS: `~/Library/Application Support/devos/config.json`
- Windows: `%APPDATA%\devos\config.json`

2. **Edit configuration:**

```bash
# Linux/macOS
nano ~/.config/devos/config.json

# Windows
notepad %APPDATA%\devos\config.json
```

### Configuration Options

```json
{
  "os": "linux",
  "ai_provider": "ollama",
  "model": "llama3.2",
  "api_key": "",
  "base_url": "http://localhost:11434",
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
  "plugins": [],
  "memory_size": 100
}
```

### LLM Provider Setup

#### Ollama (Local)

1. **Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

2. **Pull a model:**
```bash
ollama pull llama3.2
```

3. **Start Ollama:**
```bash
ollama serve
```

4. **Configure DevOS:**
```json
{
  "ai_provider": "ollama",
  "model": "llama3.2",
  "base_url": "http://localhost:11434"
}
```

#### OpenAI

```json
{
  "ai_provider": "openai",
  "model": "gpt-4",
  "api_key": "sk-..."
}
```

Or set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

#### Anthropic Claude

```json
{
  "ai_provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "api_key": "sk-ant-..."
}
```

Or set environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

#### Google Gemini

```json
{
  "ai_provider": "gemini",
  "model": "gemini-pro",
  "api_key": "..."
}
```

Or set environment variable:
```bash
export GOOGLE_API_KEY="..."
```

---

## Docker Deployment

### Basic Docker Run

```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  -v devos_config:/root/.config/devos \
  devosai/devos:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  devos:
    image: devosai/devos:latest
    container_name: devos
    volumes:
      - ./:/workspace
      - devos_config:/root/.config/devos
      - devos_logs:/root/.local/share/devos/logs
    environment:
      - DEVOS_LOG_LEVEL=info
      - DEVOS_AI_PROVIDER=ollama
    working_dir: /workspace
    stdin_open: true
    tty: true
    networks:
      - devos-network

  ollama:
    image: ollama/ollama:latest
    container_name: devos-ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - devos-network

volumes:
  devos_config:
  devos_logs:
  ollama_data:

networks:
  devos-network:
    driver: bridge
```

**Run:**
```bash
docker-compose up -d
docker-compose exec devos devos
```

### Building Custom Docker Image

Create `Dockerfile.custom`:

```dockerfile
FROM devosai/devos:latest

# Copy custom plugins
COPY my-plugins/ /root/.config/devos/plugins/

# Set custom configuration
COPY config.json /root/.config/devos/config.json

# Install additional Python packages
RUN pip install my-custom-package
```

**Build:**
```bash
docker build -f Dockerfile.custom -t my-devos:latest .
```

---

## Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/devos.service`:

```ini
[Unit]
Description=DevOS AI-Native Developer Operating Layer
After=network.target

[Service]
Type=simple
User=devos
Group=devos
WorkingDirectory=/home/devos
ExecStart=/usr/local/bin/devos
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/devos/.config/devos /home/devos/.local/share/devos

# Resource limits
LimitAS=1G
LimitRSS=500M
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo useradd -r -s /bin/false devos
sudo mkdir -p /home/devos/.config/devos
sudo chown -R devos:devos /home/devos

sudo systemctl daemon-reload
sudo systemctl enable devos
sudo systemctl start devos

# Check status
sudo systemctl status devos
sudo journalctl -u devos -f
```

### Kubernetes Deployment

Create `devos-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devos
  labels:
    app: devos
spec:
  replicas: 1
  selector:
    matchLabels:
      app: devos
  template:
    metadata:
      labels:
        app: devos
    spec:
      containers:
      - name: devos
        image: devosai/devos:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        env:
        - name: DEVOS_LOG_LEVEL
          value: "info"
        volumeMounts:
        - name: config
          mountPath: /root/.config/devos
        - name: workspace
          mountPath: /workspace
      volumes:
      - name: config
        configMap:
          name: devos-config
      - name: workspace
        emptyDir: {}
```

**Deploy:**
```bash
kubectl apply -f devos-deployment.yaml
```

### Reverse Proxy (Nginx)

For web interface (if applicable):

```nginx
server {
    listen 80;
    server_name devos.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Monitoring & Logging

### Health Monitoring

DevOS provides built-in health monitoring:

```bash
# Check health
devos> health
```

**Metrics exposed:**
- System status (healthy/degraded)
- Uptime
- Commands executed
- Error count
- Average latency

### Log Files

**Location:**
- Linux: `~/.local/share/devos/logs/`
- macOS: `~/Library/Logs/devos/`
- Windows: `%APPDATA%\devos\logs\`

**Log format:**
```
[2024-01-15 10:30:45] [INFO] [file.go:123] Message
```

### Integration with Monitoring Systems

#### Prometheus (Future)

Metrics endpoint will be available at `/metrics`.

#### Grafana Dashboard

Import dashboard JSON (available in `monitoring/grafana-dashboard.json`).

### Log Rotation

**Linux (logrotate):**

Create `/etc/logrotate.d/devos`:

```
/home/*/.local/share/devos/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 user user
}
```

---

## Security Hardening

### 1. Run as Non-Root User

```bash
sudo useradd -r -s /bin/false devos
sudo chown -R devos:devos /home/devos/.config/devos
```

### 2. Enable Sandbox Mode

```json
{
  "sandbox_mode": true,
  "blocked_commands": [
    "rm -rf /",
    "dd if=",
    "mkfs",
    "format",
    ":(){:|:&};:",
    "curl.*\|.*bash",
    "wget.*\|.*sh"
  ]
}
```

### 3. API Key Security

**Never hardcode API keys!** Use:
- Environment variables
- Secret management tools (Vault, AWS Secrets Manager)
- Kubernetes secrets

**Example with Docker:**
```bash
docker run -e OPENAI_API_KEY="$OPENAI_API_KEY" devosai/devos
```

### 4. Network Security

- Use firewall rules to restrict access
- Run Ollama on localhost only
- Use HTTPS for API calls

### 5. File Permissions

```bash
chmod 600 ~/.config/devos/config.json
chmod 700 ~/.config/devos
```

### 6. Regular Updates

```bash
# Update DevOS
pip install --upgrade devos-ai

# Update Ollama models
ollama pull llama3.2

# Update system packages
sudo apt update && sudo apt upgrade
```

---

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Check firewall
sudo ufw allow 11434/tcp
```

#### 2. "Permission denied"

**Solution:**
```bash
# Fix permissions
chmod 755 /usr/local/bin/devos
chown -R $USER:$USER ~/.config/devos
```

#### 3. "Rate limit exceeded"

**Solution:**
- Wait before making more requests
- Adjust rate limit in configuration
- Use different LLM provider

#### 4. High Memory Usage

**Solution:**
- Lower `max_tokens` in config
- Use smaller model
- Enable memory cleanup

#### 5. Slow Response Times

**Solution:**
- Use local LLM (Ollama) instead of cloud
- Check network connection
- Reduce `max_tokens`

### Debug Mode

Enable debug logging:

```json
{
  "log_level": "debug"
}
```

Or set environment variable:
```bash
export DEVOS_LOG_LEVEL=debug
devos
```

### Getting Help

1. Check logs: `~/.local/share/devos/logs/`
2. Run health check: `devos> health`
3. Check configuration: `devos> config`
4. Enable debug mode
5. Open an issue on GitHub

---

## Best Practices

1. **Regular Backups**
   - Backup `~/.config/devos/`
   - Backup SQLite database

2. **Version Control**
   - Track configuration changes
   - Use infrastructure as code

3. **Testing**
   - Test in staging environment first
   - Validate commands before production

4. **Documentation**
   - Document custom configurations
   - Keep deployment notes

5. **Security**
   - Regular security audits
   - Keep dependencies updated
   - Monitor access logs

---

For more information, visit:
- Documentation: https://docs.devos.ai
- GitHub: https://github.com/devos-ai/devos
- Issues: https://github.com/devos-ai/devos/issues
