package logger

import (
	"strings"
	"testing"
)

func TestNew(t *testing.T) {
	log := New("debug")
	if log == nil {
		t.Error("Expected logger to be created")
	}
	defer log.Close()
}

func TestLogLevels(t *testing.T) {
	log := New("debug")
	defer log.Close()

	log.Debug("debug message")
	log.Info("info message")
	log.Warn("warn message")
	log.Error("error message")
}

func TestParseLevel(t *testing.T) {
	tests := []struct {
		input    string
		expected LogLevel
	}{
		{"debug", DEBUG},
		{"info", INFO},
		{"warn", WARN},
		{"error", ERROR},
		{"invalid", INFO},
		{"", INFO},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			got := parseLevel(tt.input)
			if got != tt.expected {
				t.Errorf("parseLevel(%s) = %v, want %v", tt.input, got, tt.expected)
			}
		})
	}
}

func TestLevelString(t *testing.T) {
	tests := []struct {
		level    LogLevel
		expected string
	}{
		{DEBUG, "DEBUG"},
		{INFO, "INFO"},
		{WARN, "WARN"},
		{ERROR, "ERROR"},
		{LogLevel(999), "UNKNOWN"},
	}

	for _, tt := range tests {
		t.Run(tt.expected, func(t *testing.T) {
			got := levelString(tt.level)
			if got != tt.expected {
				t.Errorf("levelString(%v) = %s, want %s", tt.level, got, tt.expected)
			}
		})
	}
}

func TestClose(t *testing.T) {
	log := New("debug")

	err := log.Close()
	if err != nil {
		t.Errorf("Close() error = %v", err)
	}

	log.Debug("should not panic after close")
	log.Info("should not panic after close")
}

func TestGetLogDir(t *testing.T) {
	logDir, err := getLogDir()
	if err != nil {
		t.Errorf("getLogDir() error = %v", err)
	}

	if logDir == "" {
		t.Error("getLogDir() returned empty string")
	}

	if !strings.Contains(logDir, "devos") {
		t.Error("getLogDir() should contain 'devos'")
	}
}
