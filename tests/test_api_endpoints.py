"""
Tests for /health and /chat API endpoints
Validates API contract compliance and error handling
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask
from server.cit_server import app


def test_health_endpoint():
    """Test /health endpoint returns correct schema"""
    print("Testing /health endpoint...")
    
    with app.test_client() as client:
        response = client.get('/health')
        
        # Check status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Parse JSON response
        data = response.get_json()
        
        # Verify all required fields are present
        required_fields = ['ok', 'service', 'time', 'port', 'model', 'openai']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify field types and values
        assert data['ok'] is True, "ok should be True"
        assert data['service'] == 'cit', f"service should be 'cit', got {data['service']}"
        assert isinstance(data['time'], str), "time should be a string"
        assert isinstance(data['port'], int), "port should be an integer"
        assert isinstance(data['model'], str), "model should be a string"
        assert isinstance(data['openai'], bool), "openai should be a boolean"
        
        # Verify timestamp format (ISO 8601 with timezone)
        assert 'T' in data['time'], "time should be in ISO 8601 format"
        assert data['time'].endswith('Z') or '+' in data['time'] or '-' in data['time'].split('T')[-1], \
            "time should include timezone info (Z or offset)"
        
        print(f"✓ /health endpoint returns correct schema")
        print(f"  Response: {json.dumps(data, indent=2)}")


def test_chat_endpoint_valid_message():
    """Test /chat endpoint with valid message"""
    print("\nTesting /chat endpoint with valid message...")
    
    with app.test_client() as client:
        response = client.post(
            '/chat',
            data=json.dumps({'message': 'Hello'}),
            content_type='application/json'
        )
        
        # Parse JSON response
        data = response.get_json()
        
        # Verify all required fields are present
        required_fields = ['ok', 'cit', 'time', 'model', 'reply']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(data['ok'], bool), "ok should be a boolean"
        assert isinstance(data['cit'], str), "cit should be a string"
        assert isinstance(data['time'], str), "time should be a string"
        assert isinstance(data['model'], str), "model should be a string"
        assert isinstance(data['reply'], str), "reply should be a string"
        
        # Without API key, should get fallback response
        assert data['ok'] is True, "ok should be True even without API key"
        assert data['cit'] == 'fallback', "cit should be 'fallback' without API key"
        assert 'not configured' in data['reply'].lower() or 'openai' in data['reply'].lower(), \
            "reply should mention API key configuration"
        
        print(f"✓ /chat endpoint handles valid message correctly (fallback mode)")
        print(f"  Response: {json.dumps(data, indent=2)}")


def test_chat_endpoint_empty_message():
    """Test /chat endpoint with empty message (should succeed with hint)"""
    print("\nTesting /chat endpoint with empty message...")
    
    with app.test_client() as client:
        response = client.post(
            '/chat',
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )
        
        # Parse JSON response
        data = response.get_json()
        
        # Should succeed with a hint, not fail
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data['ok'] is True, "ok should be True for empty message"
        assert data['cit'] == 'hint', "cit should be 'hint' for empty message"
        assert 'hint' in data['reply'].lower() or 'provide' in data['reply'].lower(), \
            "reply should provide a helpful hint"
        
        print(f"✓ /chat endpoint handles empty message gracefully (returns hint, not error)")
        print(f"  Response: {json.dumps(data, indent=2)}")


def test_chat_endpoint_whitespace_message():
    """Test /chat endpoint with whitespace-only message"""
    print("\nTesting /chat endpoint with whitespace-only message...")
    
    with app.test_client() as client:
        response = client.post(
            '/chat',
            data=json.dumps({'message': '   '}),
            content_type='application/json'
        )
        
        # Parse JSON response
        data = response.get_json()
        
        # Should succeed with a hint, not fail
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data['ok'] is True, "ok should be True for whitespace message"
        assert data['cit'] == 'hint', "cit should be 'hint' for whitespace message"
        
        print(f"✓ /chat endpoint handles whitespace-only message gracefully")


def test_chat_endpoint_missing_message_field():
    """Test /chat endpoint with no message field"""
    print("\nTesting /chat endpoint with no message field...")
    
    with app.test_client() as client:
        response = client.post(
            '/chat',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Parse JSON response
        data = response.get_json()
        
        # Should return hint for missing message
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data['ok'] is True, "ok should be True"
        assert data['cit'] == 'hint', "cit should be 'hint'"
        
        print(f"✓ /chat endpoint handles missing message field gracefully")


def test_chat_endpoint_invalid_json():
    """Test /chat endpoint with invalid JSON"""
    print("\nTesting /chat endpoint with invalid JSON...")
    
    with app.test_client() as client:
        response = client.post(
            '/chat',
            data='',
            content_type='application/json'
        )
        
        # Parse JSON response
        data = response.get_json()
        
        # Should return error for invalid JSON
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert data['ok'] is False, "ok should be False for invalid JSON"
        assert 'json' in data['reply'].lower(), "reply should mention JSON"
        
        print(f"✓ /chat endpoint handles invalid JSON with proper error")


def test_existing_ci1_endpoint():
    """Test that existing /ci1 endpoint still works"""
    print("\nTesting existing /ci1 endpoint...")
    
    with app.test_client() as client:
        response = client.get('/ci1')
        
        # Check status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Parse JSON response
        data = response.get_json()
        
        # Verify expected fields
        assert 'system' in data, "Missing 'system' field"
        assert 'registry_id' in data, "Missing 'registry_id' field"
        assert data['system'] == 'Cimeika (CIT)', "system should be 'Cimeika (CIT)'"
        
        print(f"✓ Existing /ci1 endpoint still works correctly")


def test_restart_endpoint():
    """Test /restart endpoint returns correct schema and only accepts POST"""
    print("\nTesting /restart endpoint...")
    
    with app.test_client() as client:
        # POST should return restart confirmation
        response = client.post('/restart')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.get_json()
        
        required_fields = ['ok', 'service', 'time', 'action', 'message']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        assert data['ok'] is True, "ok should be True"
        assert data['service'] == 'cit', "service should be 'cit'"
        assert data['action'] == 'restart', "action should be 'restart'"
        assert isinstance(data['message'], str), "message should be a string"
        
        print(f"✓ /restart endpoint returns correct schema")
        print(f"  Response: {json.dumps(data, indent=2)}")


def test_restart_endpoint_rejects_get():
    """Test /restart endpoint rejects GET requests"""
    print("\nTesting /restart endpoint rejects GET...")
    
    with app.test_client() as client:
        response = client.get('/restart')
        assert response.status_code == 405, f"Expected 405, got {response.status_code}"
        
        print(f"✓ /restart endpoint correctly rejects GET requests")


def run_all_tests():
    """Run all test functions"""
    print("=" * 60)
    print("Running API Endpoint Tests")
    print("=" * 60)
    
    tests = [
        test_health_endpoint,
        test_chat_endpoint_valid_message,
        test_chat_endpoint_empty_message,
        test_chat_endpoint_whitespace_message,
        test_chat_endpoint_missing_message_field,
        test_chat_endpoint_invalid_json,
        test_existing_ci1_endpoint,
        test_restart_endpoint,
        test_restart_endpoint_rejects_get,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
