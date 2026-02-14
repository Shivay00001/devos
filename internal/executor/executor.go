package executor

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"sync"
	"time"

	"devos/internal/config"
	"devos/internal/logger"
)

type ExecutionResult struct {
	Output            string   `json:"output"`
	Commands          []string `json:"commands"`
	NeedsConfirmation bool     `json:"needs_confirmation"`
	Error             string   `json:"error,omitempty"`
}

type Executor struct {
	config *config.Config
	logger *logger.Logger
	mutex  sync.RWMutex
	closed bool
	ctx    context.Context
	cancel context.CancelFunc
}

func New(cfg *config.Config, log *logger.Logger) (*Executor, error) {
	ctx, cancel := context.WithCancel(context.Background())

	return &Executor{
		config: cfg,
		logger: log,
		ctx:    ctx,
		cancel: cancel,
	}, nil
}

func (e *Executor) Close() error {
	e.mutex.Lock()
	defer e.mutex.Unlock()

	if e.closed {
		return nil
	}

	e.closed = true
	e.cancel()
	return nil
}

func (e *Executor) Execute(input string) (*ExecutionResult, error) {
	e.mutex.RLock()
	if e.closed {
		e.mutex.RUnlock()
		return nil, fmt.Errorf("executor is closed")
	}
	e.mutex.RUnlock()

	e.logger.Info("Executing command: %s", input)

	ctx, cancel := context.WithTimeout(e.ctx, 120*time.Second)
	defer cancel()

	result, err := e.callAIEngine(ctx, input)
	if err != nil {
		return nil, fmt.Errorf("AI engine error: %w", err)
	}

	if err := e.validateCommands(result.Commands); err != nil {
		return nil, fmt.Errorf("security validation failed: %w", err)
	}

	return result, nil
}

func (e *Executor) ExecuteCommands(commands []string) error {
	e.mutex.RLock()
	if e.closed {
		e.mutex.RUnlock()
		return fmt.Errorf("executor is closed")
	}
	e.mutex.RUnlock()

	for i, cmdStr := range commands {
		e.logger.Info("Executing command %d/%d: %s", i+1, len(commands), cmdStr)

		output, err := e.executeShellCommand(cmdStr)
		if err != nil {
			e.logger.Error("Command failed: %s - Error: %v", cmdStr, err)
			return fmt.Errorf("command failed: %s - %w", cmdStr, err)
		}

		if output != "" {
			fmt.Printf("  Output: %s\n", output)
		}
	}

	return nil
}

func (e *Executor) callAIEngine(ctx context.Context, input string) (*ExecutionResult, error) {
	request := map[string]interface{}{
		"input":       input,
		"os":          e.config.OS,
		"provider":    e.config.AIProvider,
		"model":       e.config.Model,
		"api_key":     e.config.APIKey,
		"base_url":    e.config.BaseURL,
		"max_tokens":  e.config.MaxTokens,
		"temperature": e.config.Temperature,
	}

	requestData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Determine python command
	pythonCmd := "python3"
	if e.config.OS == "windows" {
		pythonCmd = "python"
		// Check if .venv exists
		if _, err := os.Stat(".venv/Scripts/python.exe"); err == nil {
			pythonCmd = ".venv/Scripts/python.exe"
		}
	}

	cmd := exec.CommandContext(ctx, pythonCmd, "-m", "ai_engine.core.processor", string(requestData))

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		return nil, fmt.Errorf("AI engine execution failed: %w - stderr: %s", err, stderr.String())
	}

	var result ExecutionResult
	if err := json.Unmarshal(stdout.Bytes(), &result); err != nil {
		return nil, fmt.Errorf("failed to parse AI response: %w - output: %s", err, stdout.String())
	}

	return &result, nil
}

func (e *Executor) validateCommands(commands []string) error {
	if !e.config.SandboxMode {
		return nil
	}

	for _, cmd := range commands {
		for _, blocked := range e.config.BlockedCommands {
			if strings.Contains(strings.ToLower(cmd), strings.ToLower(blocked)) {
				return fmt.Errorf("blocked command detected: %s", blocked)
			}
		}

		if e.isDangerous(cmd) {
			return fmt.Errorf("potentially dangerous command detected: %s", cmd)
		}
	}

	return nil
}

func (e *Executor) isDangerous(cmd string) bool {
	dangerousPatterns := []string{
		`rm\s+-rf\s+/($|\s)`,
		`rm\s+-fr\s+/($|\s)`,
		`mkfs`,
		`dd\s+if=`,
		`format`,
		`>\s*/dev/`,
		`curl.*\|\s*(bash|sh)`,
		`wget.*\|\s*(bash|sh)`,
	}

	cmdLower := strings.ToLower(cmd)
	for _, pattern := range dangerousPatterns {
		matched, _ := regexp.MatchString("(?i)"+pattern, cmdLower)
		if matched {
			return true
		}
	}

	return false
}

func (e *Executor) executeShellCommand(cmdStr string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	var cmd *exec.Cmd

	switch e.config.OS {
	case "windows":
		cmd = exec.CommandContext(ctx, "powershell", "-Command", cmdStr)
	case "darwin", "linux":
		cmd = exec.CommandContext(ctx, "sh", "-c", cmdStr)
	default:
		return "", fmt.Errorf("unsupported OS: %s", e.config.OS)
	}

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	output := strings.TrimSpace(stdout.String())

	if err != nil {
		errOutput := strings.TrimSpace(stderr.String())
		if errOutput != "" {
			return "", fmt.Errorf("%s: %s", err, errOutput)
		}
		return "", err
	}

	return output, nil
}
