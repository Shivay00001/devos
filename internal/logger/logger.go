package logger

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"sync"
	"time"
)

type LogLevel int

const (
	DEBUG LogLevel = iota
	INFO
	WARN
	ERROR
)

type Logger struct {
	level      LogLevel
	fileLogger *log.Logger
	file       *os.File
	mutex      sync.RWMutex
	closed     bool
}

func New(levelStr string) *Logger {
	level := parseLevel(levelStr)

	logDir, err := getLogDir()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Warning: failed to get log directory: %v\n", err)
		return &Logger{level: level}
	}

	if err := os.MkdirAll(logDir, 0755); err != nil {
		fmt.Fprintf(os.Stderr, "Warning: failed to create log directory: %v\n", err)
		return &Logger{level: level}
	}

	logFile := filepath.Join(logDir, fmt.Sprintf("devos-%s.log", time.Now().Format("2006-01-02")))
	file, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Warning: failed to open log file: %v\n", err)
		return &Logger{level: level}
	}

	var writer io.Writer
	if level == DEBUG {
		writer = io.MultiWriter(file, os.Stdout)
	} else {
		writer = file
	}

	return &Logger{
		level:      level,
		fileLogger: log.New(writer, "", 0),
		file:       file,
	}
}

func (l *Logger) Close() error {
	l.mutex.Lock()
	defer l.mutex.Unlock()

	if l.closed {
		return nil
	}

	l.closed = true
	if l.file != nil {
		return l.file.Close()
	}
	return nil
}

func (l *Logger) Debug(format string, args ...interface{}) {
	l.mutex.RLock()
	if l.closed {
		l.mutex.RUnlock()
		return
	}
	l.mutex.RUnlock()

	if l.level <= DEBUG {
		l.log(DEBUG, format, args...)
	}
}

func (l *Logger) Info(format string, args ...interface{}) {
	l.mutex.RLock()
	if l.closed {
		l.mutex.RUnlock()
		return
	}
	l.mutex.RUnlock()

	if l.level <= INFO {
		l.log(INFO, format, args...)
	}
}

func (l *Logger) Warn(format string, args ...interface{}) {
	l.mutex.RLock()
	if l.closed {
		l.mutex.RUnlock()
		return
	}
	l.mutex.RUnlock()

	if l.level <= WARN {
		l.log(WARN, format, args...)
	}
}

func (l *Logger) Error(format string, args ...interface{}) {
	l.mutex.RLock()
	if l.closed {
		l.mutex.RUnlock()
		return
	}
	l.mutex.RUnlock()

	if l.level <= ERROR {
		l.log(ERROR, format, args...)
	}
}

func (l *Logger) log(level LogLevel, format string, args ...interface{}) {
	if l.fileLogger == nil {
		return
	}

	_, file, line, ok := runtime.Caller(2)
	caller := "unknown"
	if ok {
		caller = fmt.Sprintf("%s:%d", filepath.Base(file), line)
	}

	timestamp := time.Now().Format("2006-01-02 15:04:05")
	levelStr := levelString(level)
	message := fmt.Sprintf(format, args...)

	logLine := fmt.Sprintf("[%s] [%s] [%s] %s", timestamp, levelStr, caller, message)

	l.fileLogger.Println(logLine)
}

func parseLevel(level string) LogLevel {
	switch level {
	case "debug":
		return DEBUG
	case "info":
		return INFO
	case "warn":
		return WARN
	case "error":
		return ERROR
	default:
		return INFO
	}
}

func levelString(level LogLevel) string {
	switch level {
	case DEBUG:
		return "DEBUG"
	case INFO:
		return "INFO"
	case WARN:
		return "WARN"
	case ERROR:
		return "ERROR"
	default:
		return "UNKNOWN"
	}
}

func getLogDir() (string, error) {
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
		baseDir = filepath.Join(home, "Library", "Logs")
	default:
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		baseDir = filepath.Join(home, ".local", "share")
	}

	return filepath.Join(baseDir, "devos", "logs"), nil
}
