"""
Test to verify MemoryEntry structure for task 2.4.5.

This test explicitly verifies that the long_term_memory structure
stores objects with text and weight fields as required by Requirements 2.11.
"""

import pytest
from datetime import datetime
from models import MemoryEntry, UserData


class TestMemoryEntryStructure:
    """Test suite for MemoryEntry structure validation."""
    
    def test_memory_entry_has_text_and_weight_fields(self):
        """Verify MemoryEntry has text and weight fields."""
        # Create a MemoryEntry
        memory = MemoryEntry(
            text="User likes pizza",
            weight=0.9
        )
        
        # Verify fields exist and have correct values
        assert hasattr(memory, 'text')
        assert hasattr(memory, 'weight')
        assert memory.text == "User likes pizza"
        assert memory.weight == 0.9
    
    def test_memory_entry_weight_range(self):
        """Verify weight is constrained to 0.0-1.0 range."""
        # Valid weights
        memory1 = MemoryEntry(text="Test", weight=0.0)
        assert memory1.weight == 0.0
        
        memory2 = MemoryEntry(text="Test", weight=1.0)
        assert memory2.weight == 1.0
        
        memory3 = MemoryEntry(text="Test", weight=0.5)
        assert memory3.weight == 0.5
        
        # Invalid weights should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            MemoryEntry(text="Test", weight=-0.1)
        
        with pytest.raises(Exception):  # Pydantic validation error
            MemoryEntry(text="Test", weight=1.1)
    
    def test_user_data_long_term_memory_uses_memory_entry(self):
        """Verify UserData.long_term_memory uses MemoryEntry objects."""
        # Create UserData with long_term_memory
        user = UserData(
            user_id="test_user",
            long_term_memory=[
                MemoryEntry(text="Memory 1", weight=0.8),
                MemoryEntry(text="Memory 2", weight=0.6),
            ]
        )
        
        # Verify long_term_memory contains MemoryEntry objects
        assert len(user.long_term_memory) == 2
        assert isinstance(user.long_term_memory[0], MemoryEntry)
        assert isinstance(user.long_term_memory[1], MemoryEntry)
        
        # Verify each entry has text and weight
        assert user.long_term_memory[0].text == "Memory 1"
        assert user.long_term_memory[0].weight == 0.8
        assert user.long_term_memory[1].text == "Memory 2"
        assert user.long_term_memory[1].weight == 0.6
    
    def test_memory_entry_serialization(self):
        """Verify MemoryEntry can be serialized to dict for Firestore."""
        memory = MemoryEntry(
            text="Important memory",
            weight=0.95
        )
        
        # Convert to dict
        memory_dict = memory.model_dump()
        
        # Verify dict structure
        assert "text" in memory_dict
        assert "weight" in memory_dict
        assert memory_dict["text"] == "Important memory"
        assert memory_dict["weight"] == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
