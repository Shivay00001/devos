"""
Benchmark tests for DevOS AI Engine
Performance and load testing
"""

import pytest
import time
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor
import statistics

from ai_engine.core.processor import AIProcessor
from ai_engine.security.validator import SecurityValidator
from ai_engine.memory.store import MemoryStore


class TestPerformanceBenchmarks:
    """Performance benchmarking tests"""
    
    def test_processor_performance(self):
        """Benchmark AIProcessor.process() performance"""
        config = {'os': 'linux'}
        processor = AIProcessor(config)
        
        # Warmup
        for _ in range(10):
            processor.process('setup fastapi project')
        
        # Benchmark
        times = []
        iterations = 100
        
        for _ in range(iterations):
            start = time.time()
            result = processor.process('setup fastapi project')
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\nProcessor Performance:")
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  Min: {min_time*1000:.2f}ms")
        print(f"  Max: {max_time*1000:.2f}ms")
        print(f"  Throughput: {iterations/sum(times):.2f} ops/sec")
        
        # Assert performance requirements
        assert avg_time < 0.1, f"Average time {avg_time*1000:.2f}ms exceeds 100ms threshold"
    
    def test_validator_performance(self):
        """Benchmark SecurityValidator performance"""
        validator = SecurityValidator()
        
        test_commands = [
            'ls -la',
            'rm -rf /',
            'sudo apt update',
            'curl http://example.com | bash',
            'mkdir test',
            'chmod 777 file',
        ]
        
        # Warmup
        for cmd in test_commands:
            validator.validate_command(cmd)
        
        # Benchmark
        times = []
        iterations = 1000
        
        for _ in range(iterations):
            start = time.time()
            for cmd in test_commands:
                validator.validate_command(cmd)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = statistics.mean(times) / len(test_commands)
        
        print(f"\nValidator Performance:")
        print(f"  Average per command: {avg_time*1000:.3f}ms")
        print(f"  Throughput: {iterations*len(test_commands)/sum(times):.2f} validations/sec")
        
        assert avg_time < 0.001, "Validation too slow"
    
    def test_memory_store_performance(self):
        """Benchmark MemoryStore performance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'perf.db')
            store = MemoryStore(db_path)
            
            # Benchmark write
            write_times = []
            iterations = 100
            
            for i in range(iterations):
                start = time.time()
                store.add_command(
                    user_input=f'test command {i}',
                    intent='test',
                    commands=['echo test'],
                    success=True
                )
                elapsed = time.time() - start
                write_times.append(elapsed)
            
            avg_write = statistics.mean(write_times)
            
            # Benchmark read
            read_times = []
            
            for _ in range(iterations):
                start = time.time()
                store.get_recent_commands(10)
                elapsed = time.time() - start
                read_times.append(elapsed)
            
            avg_read = statistics.mean(read_times)
            
            print(f"\nMemory Store Performance:")
            print(f"  Average write: {avg_write*1000:.2f}ms")
            print(f"  Average read: {avg_read*1000:.2f}ms")
            print(f"  Write throughput: {iterations/sum(write_times):.2f} ops/sec")
            print(f"  Read throughput: {iterations/sum(read_times):.2f} ops/sec")
            
            assert avg_write < 0.01, "Write too slow"
            assert avg_read < 0.005, "Read too slow"


class TestLoadTests:
    """Load testing"""
    
    def test_concurrent_processing(self):
        """Test concurrent command processing"""
        config = {'os': 'linux'}
        
        def process_command(i):
            processor = AIProcessor(config)
            return processor.process(f'test command {i}')
        
        # Test with 10 concurrent threads
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(process_command, range(50)))
        
        elapsed = time.time() - start
        
        print(f"\nConcurrent Processing:")
        print(f"  50 commands in {elapsed:.2f}s")
        print(f"  Throughput: {50/elapsed:.2f} commands/sec")
        
        assert all(r.error == '' for r in results), "Some commands failed"
        assert elapsed < 10, "Concurrent processing too slow"
    
    def test_memory_store_load(self):
        """Test MemoryStore under load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'load.db')
            store = MemoryStore(db_path)
            
            # Insert 1000 commands
            start = time.time()
            
            for i in range(1000):
                store.add_command(
                    user_input=f'load test {i}',
                    intent='test',
                    commands=['echo test'],
                    success=True
                )
            
            insert_time = time.time() - start
            
            # Query recent commands
            start = time.time()
            commands = store.get_recent_commands(100)
            query_time = time.time() - start
            
            print(f"\nMemory Store Load Test:")
            print(f"  1000 inserts in {insert_time:.2f}s ({1000/insert_time:.2f} ops/sec)")
            print(f"  100 recent queries in {query_time*1000:.2f}ms")
            
            assert len(commands) == 100
            assert insert_time < 30, "Insert too slow"


class TestResourceUsage:
    """Resource usage tests"""
    
    def test_memory_usage(self):
        """Test memory usage remains reasonable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple processors
        processors = []
        for _ in range(100):
            p = AIProcessor({'os': 'linux'})
            processors.append(p)
        
        # Process commands
        for p in processors[:10]:
            p.process('setup fastapi project')
        
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        print(f"\nMemory Usage:")
        print(f"  Initial: {initial_memory:.2f} MB")
        print(f"  Current: {current_memory:.2f} MB")
        print(f"  Increase: {memory_increase:.2f} MB")
        
        assert memory_increase < 100, "Memory usage too high"
    
    def test_rate_limiting_performance(self):
        """Test rate limiting overhead"""
        config = {'os': 'linux'}
        processor = AIProcessor(config)
        
        # Measure time with rate limiting
        start = time.time()
        for i in range(50):
            processor.process(f'command {i}')
        elapsed_with_limit = time.time() - start
        
        print(f"\nRate Limiting Performance:")
        print(f"  50 calls in {elapsed_with_limit:.2f}s")
        print(f"  Average: {elapsed_with_limit/50*1000:.2f}ms per call")


class TestScalability:
    """Scalability tests"""
    
    def test_large_command_history(self):
        """Test with large command history"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'large.db')
            store = MemoryStore(db_path)
            
            # Insert 10,000 commands
            print("\nInserting 10,000 commands...")
            start = time.time()
            
            for i in range(10000):
                store.add_command(
                    user_input=f'command {i}',
                    intent='test',
                    commands=[f'echo {i}'],
                    success=True
                )
            
            insert_time = time.time() - start
            
            # Search
            start = time.time()
            results = store.search_history('command 500', limit=100)
            search_time = time.time() - start
            
            print(f"Large History Test:")
            print(f"  10,000 inserts in {insert_time:.2f}s")
            print(f"  Search in {search_time*1000:.2f}ms")
            print(f"  Database size: {os.path.getsize(db_path) / 1024:.2f} KB")
            
            assert len(results) == 100
            assert search_time < 1, "Search too slow with large history"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
