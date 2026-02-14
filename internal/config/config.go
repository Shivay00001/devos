package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
)

const Version = "0.1.0"

type Config struct {
	OS               string   `json:"os"`
	ConfigPath       string   `json:"config_path"`
	AIProvider       string   `json:"ai_provider"`
	Model            string   `json:"model"`
	APIKey           string   `json:"api_key,omitempty"`
	BaseURL          string   `json:"base_url,omitempty"`
	ConfirmationMode bool     `json:"confirmation_mode"`
	LogLevel         string   `json:"log_level"`
	MaxTokens        int      `json:"max_tokens"`
	Temperature      float64  `json:"temperature"`
	SandboxMode      bool     `json:"sandbox_mode"`
	AllowedCommands  []string `json:"allowed_commands,omitempty"`
	BlockedCommands  []string `json:"blocked_commands"`
	Plugins          []string `json:"plugins"`
	PluginPath       string   `json:"plugin_path"`
	MemoryPath       string   `json:"memory_path"`
	MemorySize       int      `json:"memory_size"`
}

var DefaultConfig = Config{
	AIProvider:       "ollama",
	Model:            "llama3.2",
	ConfirmationMode: true,
	LogLevel:         "info",
	MaxTokens:        2048,
	Temperature:      0.7,
	SandboxMode:      true,
	BlockedCommands: []string{
		"rm -rf /",
		"dd if=",
		"mkfs",
		"format",
		":(){:|:&};:",
	},
	Plugins:    []string{},
	MemorySize: 100,
}

func Load() (*Config, error) {
	configDir, err := getConfigDir()
	if err != nil {
		return nil, err
	}

	configPath := filepath.Join(configDir, "config.json")

	if err := os.MkdirAll(configDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create config directory: %w", err)
	}

	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		config := DefaultConfig
		config.OS = runtime.GOOS
		config.ConfigPath = configPath
		config.PluginPath = filepath.Join(configDir, "plugins")
		config.MemoryPath = filepath.Join(configDir, "memory.db")

		if err := config.Save(); err != nil {
			return nil, fmt.Errorf("failed to save default config: %w", err)
		}

		return &config, nil
	}

	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var config Config
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to parse config file: %w", err)
	}

	config.OS = runtime.GOOS
	config.ConfigPath = configPath

	return &config, nil
}

func (c *Config) Save() error {
	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	if err := os.WriteFile(c.ConfigPath, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

func getConfigDir() (string, error) {
	var baseDir string

	switch runtime.GOOS {
	case "windows":
		baseDir = os.Getenv("APPDATA")
		if baseDir == "" {
			return "", fmt.Errorf("APPDATA environment variable not set")
		}
	case "darwin":
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		baseDir = filepath.Join(home, "Library", "Application Support")
	default:
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		xdgConfig := os.Getenv("XDG_CONFIG_HOME")
		if xdgConfig != "" {
			baseDir = xdgConfig
		} else {
			baseDir = filepath.Join(home, ".config")
		}
	}

	return filepath.Join(baseDir, "devos"), nil
}

func (c *Config) Validate() error {
	validProviders := map[string]bool{
		"openai":    true,
		"anthropic": true,
		"gemini":    true,
		"ollama":    true,
	}

	if !validProviders[c.AIProvider] {
		return fmt.Errorf("invalid AI provider: %s", c.AIProvider)
	}

	if c.AIProvider != "ollama" && c.APIKey == "" {
		return fmt.Errorf("API key required for provider: %s", c.AIProvider)
	}

	validLevels := map[string]bool{
		"debug": true,
		"info":  true,
		"warn":  true,
		"error": true,
	}

	if !validLevels[c.LogLevel] {
		return fmt.Errorf("invalid log level: %s", c.LogLevel)
	}

	return nil
}
