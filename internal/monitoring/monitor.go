package monitoring

import (
	"fmt"
	"sync"
	"time"

	"devos/internal/logger"
)

type HealthStatus struct {
	Status      string        `json:"status"`
	Uptime      time.Duration `json:"uptime"`
	CommandsRun int           `json:"commands_run"`
	ErrorCount  int           `json:"error_count"`
	AvgLatency  time.Duration `json:"avg_latency"`
}

type Monitor struct {
	logger      *logger.Logger
	startTime   time.Time
	commandsRun int
	errorCount  int
	latencies   []time.Duration
	mutex       sync.RWMutex
	stopChan    chan bool
	running     bool
}

func New(logger *logger.Logger) *Monitor {
	return &Monitor{
		logger:   logger,
		stopChan: make(chan bool),
	}
}

func (m *Monitor) Start() {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	if m.running {
		return
	}

	m.startTime = time.Now()
	m.running = true

	go m.monitorLoop()
}

func (m *Monitor) Stop() {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	if !m.running {
		return
	}

	m.running = false
	close(m.stopChan)
}

func (m *Monitor) monitorLoop() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			m.logHealth()
		case <-m.stopChan:
			return
		}
	}
}

func (m *Monitor) logHealth() {
	status := m.GetHealth()
	m.logger.Info("Health Status: Commands=%d, Errors=%d, AvgLatency=%s, Uptime=%s",
		status.CommandsRun, status.ErrorCount, status.AvgLatency, status.Uptime)
}

func (m *Monitor) RecordCommand(duration time.Duration) {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	m.commandsRun++
	m.latencies = append(m.latencies, duration)

	if len(m.latencies) > 100 {
		m.latencies = m.latencies[1:]
	}
}

func (m *Monitor) RecordError(err error) {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	m.errorCount++
	m.logger.Error("Error recorded: %v", err)
}

func (m *Monitor) GetHealth() HealthStatus {
	m.mutex.RLock()
	defer m.mutex.RUnlock()

	status := "healthy"
	if m.errorCount > 10 {
		status = "degraded"
	}

	var avgLatency time.Duration
	if len(m.latencies) > 0 {
		var total time.Duration
		for _, lat := range m.latencies {
			total += lat
		}
		avgLatency = total / time.Duration(len(m.latencies))
	}

	return HealthStatus{
		Status:      status,
		Uptime:      time.Since(m.startTime),
		CommandsRun: m.commandsRun,
		ErrorCount:  m.errorCount,
		AvgLatency:  avgLatency,
	}
}

func (m *Monitor) ResetCounters() {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	m.commandsRun = 0
	m.errorCount = 0
	m.latencies = nil
}

func (m *Monitor) GetStats() map[string]interface{} {
	m.mutex.RLock()
	defer m.mutex.RUnlock()

	var avgLatency time.Duration
	if len(m.latencies) > 0 {
		var total time.Duration
		for _, lat := range m.latencies {
			total += lat
		}
		avgLatency = total / time.Duration(len(m.latencies))
	}

	return map[string]interface{}{
		"uptime":       time.Since(m.startTime).String(),
		"commands_run": m.commandsRun,
		"error_count":  m.errorCount,
		"avg_latency":  fmt.Sprintf("%v", avgLatency),
		"running":      m.running,
	}
}
