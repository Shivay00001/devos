# Contributing to DevOS

Thank you for your interest in contributing to DevOS! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Go 1.21+
- Python 3.8+
- Git

### Local Development

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/devos.git
   cd devos
   ```

3. Install Go dependencies:
   ```bash
   go mod download
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8 mypy
   ```

5. Run tests:
   ```bash
   # Go tests
   go test -v ./...
   
   # Python tests
   pytest tests/ -v
   ```

## Project Structure

```
devos/
├── cmd/devos/          # Go CLI entry point
├── internal/           # Go internal packages
│   ├── config/
│   ├── executor/
│   ├── logger/
│   └── monitoring/
├── ai_engine/          # Python AI engine
│   ├── core/
│   ├── adapters/
│   ├── security/
│   └── plugins/
├── adapters/           # OS-specific adapters
├── tests/              # Test files
└── .github/workflows/  # CI/CD configuration
```

## Coding Standards

### Go

- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Use `gofmt` for formatting
- Add comments for exported functions
- Write unit tests for new functionality

### Python

- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting: `black .`
- Use `flake8` for linting: `flake8 .`
- Add type hints where appropriate
- Write unit tests with pytest

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run Go tests only
go test -v ./...

# Run Python tests only
pytest tests/ -v

# Run with coverage
go test -cover ./...
pytest --cov=ai_engine
```

### Writing Tests

- Test files should be named `*_test.go` (Go) or `test_*.py` (Python)
- Aim for >80% code coverage
- Test both success and failure cases
- Use table-driven tests where appropriate

## Pull Request Process

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git commit -m "Add feature: description"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request against the `main` branch

5. Ensure all CI checks pass

## Commit Message Guidelines

Use conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build process or auxiliary tool changes

Example:
```
feat: add support for custom AI providers

- Implement adapter pattern for LLM providers
- Add configuration validation
- Update documentation
```

## Security

- Never commit API keys or credentials
- Report security vulnerabilities privately
- Follow security best practices in your code

## Code Review

All submissions require review. We will:

- Review your code within 48 hours
- Provide constructive feedback
- Request changes if necessary
- Merge when ready

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Join our Discord community

Thank you for contributing! 🚀
