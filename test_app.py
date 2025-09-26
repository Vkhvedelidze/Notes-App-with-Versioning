#!/usr/bin/env python3
"""
Basic test suite for the Notes App with Versioning
This provides simple tests to verify core functionality
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, load_data, save_data, create_note_version
from fastapi.testclient import TestClient

class TestNotesApp(unittest.TestCase):
    """Test cases for the Notes App"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
        # Use temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.write('{"notes": {}, "versions": {}}')
        self.temp_file.close()
        
        # Patch the DATA_FILE to use our temporary file
        self.data_file_patch = patch('main.DATA_FILE', self.temp_file.name)
        self.data_file_patch.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.data_file_patch.stop()
        os.unlink(self.temp_file.name)
    
    def test_create_note(self):
        """Test creating a new note"""
        response = self.client.post("/api/notes/", json={
            "title": "Test Note",
            "content": "This is a test note content"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Test Note")
        self.assertEqual(data["content"], "This is a test note content")
        self.assertEqual(data["version"], 1)
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
    
    def test_get_notes(self):
        """Test getting all notes"""
        # First create a note
        self.client.post("/api/notes/", json={
            "title": "Test Note",
            "content": "Test content"
        })
        
        # Then get all notes
        response = self.client.get("/api/notes/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Test Note")
    
    def test_get_specific_note(self):
        """Test getting a specific note"""
        # Create a note first
        create_response = self.client.post("/api/notes/", json={
            "title": "Specific Note",
            "content": "Specific content"
        })
        note_id = create_response.json()["id"]
        
        # Get the specific note
        response = self.client.get(f"/api/notes/{note_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Specific Note")
        self.assertEqual(data["id"], note_id)
    
    def test_update_note(self):
        """Test updating a note"""
        # Create a note first
        create_response = self.client.post("/api/notes/", json={
            "title": "Original Title",
            "content": "Original content"
        })
        note_id = create_response.json()["id"]
        
        # Update the note
        response = self.client.put(f"/api/notes/{note_id}", json={
            "title": "Updated Title",
            "content": "Updated content"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Updated Title")
        self.assertEqual(data["content"], "Updated content")
        self.assertEqual(data["version"], 2)  # Version should increment
    
    def test_delete_note(self):
        """Test deleting a note"""
        # Create a note first
        create_response = self.client.post("/api/notes/", json={
            "title": "To Delete",
            "content": "This will be deleted"
        })
        note_id = create_response.json()["id"]
        
        # Delete the note
        response = self.client.delete(f"/api/notes/{note_id}")
        self.assertEqual(response.status_code, 200)
        
        # Verify it's deleted
        get_response = self.client.get(f"/api/notes/{note_id}")
        self.assertEqual(get_response.status_code, 404)
    
    def test_get_note_versions(self):
        """Test getting note versions"""
        # Create a note
        create_response = self.client.post("/api/notes/", json={
            "title": "Versioned Note",
            "content": "Version 1"
        })
        note_id = create_response.json()["id"]
        
        # Update the note to create a new version
        self.client.put(f"/api/notes/{note_id}", json={
            "title": "Versioned Note",
            "content": "Version 2"
        })
        
        # Get versions
        response = self.client.get(f"/api/notes/{note_id}/versions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)  # Should have 2 versions
        self.assertEqual(data[0]["version"], 2)  # Latest version first
        self.assertEqual(data[1]["version"], 1)
    
    def test_restore_note_version(self):
        """Test restoring a note to a previous version"""
        # Create a note
        create_response = self.client.post("/api/notes/", json={
            "title": "Restore Test",
            "content": "Original content"
        })
        note_id = create_response.json()["id"]
        
        # Update the note
        self.client.put(f"/api/notes/{note_id}", json={
            "title": "Restore Test",
            "content": "Updated content"
        })
        
        # Get versions to find the first version ID
        versions_response = self.client.get(f"/api/notes/{note_id}/versions")
        versions = versions_response.json()
        first_version_id = versions[1]["id"]  # Second item is version 1
        
        # Restore to first version
        response = self.client.post(f"/api/notes/{note_id}/restore/{first_version_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["content"], "Original content")
        self.assertEqual(data["version"], 3)  # Should be version 3 now
    
    def test_note_not_found(self):
        """Test handling of non-existent note"""
        response = self.client.get("/api/notes/non-existent-id")
        self.assertEqual(response.status_code, 404)
    
    def test_main_page_loads(self):
        """Test that the main page loads correctly"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Notes App with Versioning", response.text)

def run_tests():
    """Run all tests"""
    print("Running Notes App Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNotesApp)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("All tests passed!")
    else:
        print(f"{len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

