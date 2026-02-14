package monitoring

import (
	"errors"
	"testing"
	"time"

	"devos/internal/logger"
)

func TestNew(t *testing.T) {
	log := logger.New("debug")
	defer log.Close()

	mon := New(log)
	if mon == nil {
		t.Error("Expected monitor to be created")
	}
}

func TestStartStop(t *testing.T) {
	log := logger.New("debug")
	defer log.Close()

	mon := New(log)
	mon.Start()

	time.Sleep(100 * time.Millisecond)

	mon.Stop()

	if mon.running {
		t.Error("Monitor should be stopped")
	}
}

func TestRecordCommand(t *testing.T) {
	log := logger.New("debug")
	defer log.Close()

	mon := New(log)
	mon.Start()
	defer mon.Stop()

	mon.RecordCommand(100 * time.Millisecond)
	mon.RecordCommand(200 * time.Millisecond)

	health := mon.GetHealth()
	if health.CommandsRun != 2 {
		t.Errorf("Expected CommandsRun = 2, got %d", health.CommandsRun)
	}
}

func TestRecordError(t *testing.T) {
	log := logger.New("debug")
	defer log.Close()

	mon := New(log)
	mon.Start()
	defer mon.Stop()

	err := errors.New("test error")
	mon.RecordError(err)

	health := mon.GetHealth()
	if health.ErrorCount != 1 {
		t.Errorf("Expected ErrorCount = 1, got %d", health.ErrorCount)
	}
}

func TestGetHealth(t *testing.T) {
	log := logger.New("debug")
	defer log.Close()

	mon := New(log)
	mon.Start()
	defer mon.Stop()

	mon.RecordCommand(100 * time.Millisecond)
	mon.RecordError(errors.New("test error"))

	health := mon.GetHealth()

	if health.Status != "healthy" {
		t.Errorf("Expected status = 'healthy', got %s", health.Status)
	}

	if health.CommandsRun != 1 {
		t.Errorf("Expected CommandsRun = 1, got %d", health.CommandsRun)
	}

	if health.ErrorCount != 1 {
		t.Errorf("Expected ErrorCount = 1, got %d", health.ErrorCount)
	}
}

func TestResetCounters(t *testing.T) {
	log := logger.New("debug")
	defer log.Close()

	mon := New(log)
	mon.Start()
	defer mon.Stop()

	mon.RecordCommand(100 * time.Millisecond)
	mon.RecordError(errors.New("test error"))

	mon.ResetCounters()

	health := mon.GetHealth()
	if health.CommandsRun != 0 {
		t.Errorf("Expected CommandsRun = 0 after reset, got %d", health.CommandsRun)
	}

	if health.ErrorCount != 0 {
		t.Errorf("Expected ErrorCount = 0 after reset, got %d", health.ErrorCount)
	}
}

func TestGetStats(t *testing.T) {
	log := logger.New("debug")
	defer log.Close()

	mon := New(log)
	mon.Start()
	defer mon.Stop()

	stats := mon.GetStats()

	if _, ok := stats["uptime"]; !ok {
		t.Error("GetStats should contain 'uptime'")
	}

	if _, ok := stats["commands_run"]; !ok {
		t.Error("GetStats should contain 'commands_run'")
	}

	if _, ok := stats["running"]; !ok {
		t.Error("GetStats should contain 'running'")
	}
}
