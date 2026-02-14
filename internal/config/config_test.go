package config

import (
	"os"
	"path/filepath"
	"runtime"
	"testing"
)

func TestLoad(t *testing.T) {
	tmpDir := t.TempDir()
	originalHome := os.Getenv("HOME")
	if runtime.GOOS == "windows" {
		os.Setenv("APPDATA", tmpDir)
	} else {
		os.Setenv("HOME", tmpDir)
	}
	defer func() {
		if runtime.GOOS == "windows" {
			os.Unsetenv("APPDATA")
		} else {
			os.Setenv("HOME", originalHome)
		}
	}()

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() error = %v", err)
	}

	if cfg.AIProvider != "ollama" {
		t.Errorf("Expected AIProvider = 'ollama', got %s", cfg.AIProvider)
	}

	if cfg.Model != "llama3.2" {
		t.Errorf("Expected Model = 'llama3.2', got %s", cfg.Model)
	}
}

func TestValidate(t *testing.T) {
	tests := []struct {
		name    string
		config  Config
		wantErr bool
	}{
		{
			name: "valid ollama config",
			config: Config{
				AIProvider: "ollama",
				Model:      "llama3.2",
				LogLevel:   "info",
			},
			wantErr: false,
		},
		{
			name: "invalid provider",
			config: Config{
				AIProvider: "invalid",
				Model:      "test",
				LogLevel:   "info",
			},
			wantErr: true,
		},
		{
			name: "openai without key",
			config: Config{
				AIProvider: "openai",
				Model:      "gpt-4",
				LogLevel:   "info",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.config.Validate()
			if (err != nil) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestSave(t *testing.T) {
	tmpDir := t.TempDir()
	cfg := &Config{
		ConfigPath: filepath.Join(tmpDir, "config.json"),
		AIProvider: "ollama",
		Model:      "test-model",
	}

	err := cfg.Save()
	if err != nil {
		t.Fatalf("Save() error = %v", err)
	}

	if _, err := os.Stat(cfg.ConfigPath); os.IsNotExist(err) {
		t.Error("Config file was not created")
	}
}


