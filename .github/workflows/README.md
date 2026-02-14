# DevOS CI/CD Pipeline

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)

Triggered on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Release creation

#### Jobs:

1. **test-go**: Run Go unit tests with race detection and coverage
2. **test-python**: Run Python tests across multiple Python versions (3.8-3.11)
3. **security-scan**: Run security scanners (Gosec for Go, Bandit for Python)
4. **build**: Build binaries for Linux, Windows, and macOS
5. **docker**: Build and push Docker images
6. **release**: Create GitHub releases with artifacts
7. **notify**: Send notifications about build status

## Required Secrets

Add these secrets to your GitHub repository:

- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub access token
- `GITHUB_TOKEN`: Automatically provided by GitHub

## Local Testing

Run tests locally before pushing:

```bash
# Go tests
go test -v -race ./...

# Python tests
pytest tests/ -v

# Security scans
gosec ./...
bandit -r ai_engine

# Build
cd cmd/devos
go build -o devos .
```
