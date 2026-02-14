"""
Tests for Memory Store
"""

import pytest
import tempfile
import os
from ai_engine.memory.store import MemoryStore


class TestMemoryStore:
    """Test cases for MemoryStore"""
    
    @pytest.fixture
    def store(self):
        """Create a temporary memory store for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test_memory.db')
            store = MemoryStore(db_path)
            yield store
    
    def test_initialization(self, store):
        """Test store initialization"""
        assert store is not None
        assert os.path.exists(store.db_path)
    
    def test_add_command(self, store):
        """Test adding command to history"""
        record_id = store.add_command(
            user_input="test command",
            intent="test",
            commands=["echo test"],
            success=True,
            output="test output"
        )
        
        assert record_id is not None
        assert isinstance(record_id, int)
    
    def test_get_recent_commands(self, store):
        """Test retrieving recent commands"""
        # Add some commands
        store.add_command("cmd1", "test", ["cmd1"], True)
        store.add_command("cmd2", "test", ["cmd2"], True)
        store.add_command("cmd3", "test", ["cmd3"], True)
        
        # Get recent commands
        commands = store.get_recent_commands(limit=2)
        
        assert len(commands) == 2
        assert commands[0]['user_input'] == "cmd3"  # Most recent first
        assert commands[1]['user_input'] == "cmd2"
    
    def test_search_history(self, store):
        """Test searching command history"""
        # Add commands
        store.add_command("setup fastapi project", "project_setup", ["mkdir project"], True)
        store.add_command("analyze performance", "analyze", ["top"], True)
        store.add_command("setup react app", "project_setup", ["npx create-react-app"], True)
        
        # Search for setup commands
        results = store.search_history("setup")
        
        assert len(results) == 2
        
    def test_set_and_get_context(self, store):
        """Test setting and retrieving context"""
        # Set context
        store.set_context('test_key', 'test_value', category='test')
        
        # Get context
        value = store.get_context('test_key')
        
        assert value == 'test_value'
    
    def test_get_context_nonexistent(self, store):
        """Test retrieving non-existent context"""
        value = store.get_context('nonexistent_key')
        
        assert value is None
    
    def test_get_context_by_category(self, store):
        """Test retrieving context by category"""
        # Set contexts in different categories
        store.set_context('key1', 'value1', category='category1')
        store.set_context('key2', 'value2', category='category1')
        store.set_context('key3', 'value3', category='category2')
        
        # Get contexts by category
        contexts = store.get_context_by_category('category1')
        
        assert len(contexts) == 2
        assert 'key1' in contexts
        assert 'key2' in contexts
    
    def test_save_and_get_project_context(self, store):
        """Test saving and retrieving project context"""
        # Save project context
        store.save_project_context(
            project_path='/path/to/project',
            project_type='fastapi',
            dependencies=['fastapi', 'uvicorn']
        )
        
        # Get project context
        context = store.get_project_context('/path/to/project')
        
        assert context is not None
        assert context['project_type'] == 'fastapi'
        assert 'fastapi' in context['dependencies']
    
    def test_get_project_context_nonexistent(self, store):
        """Test retrieving non-existent project context"""
        context = store.get_project_context('/nonexistent/path')
        
        assert context is None
    
    def test_cleanup_old_records(self, store):
        """Test cleaning up old records"""
        # Add a command
        store.add_command("old command", "test", ["cmd"], True)
        
        # Clean up records older than 0 days (should remove all)
        store.cleanup_old_records(days=0)
        
        # Verify records are cleaned
        commands = store.get_recent_commands(limit=10)
        assert len(commands) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
