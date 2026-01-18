"""
Basic tests for CIT v2.1 components
Tests OpenAIClient and JobManager functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.openai_client import OpenAIClient
from server.jobs import JobManager
from server.job_store import JobStore


def test_openai_client_init():
    """Test OpenAIClient initialization"""
    print("Testing OpenAIClient initialization...")
    
    # Test with no API key
    client = OpenAIClient()
    assert client is not None
    assert client.model in ["gpt-4o-mini", "gpt-4.1-mini"]
    print("✓ OpenAIClient initializes correctly")
    
    # Test with custom API key and model
    client2 = OpenAIClient(api_key="test-key", model="gpt-4")
    assert client2.api_key == "test-key"
    assert client2.model == "gpt-4"
    print("✓ OpenAIClient accepts custom parameters")
    
    # Test setters
    client2.set_api_key("new-key")
    client2.set_model("gpt-3.5-turbo")
    assert client2.api_key == "new-key"
    assert client2.model == "gpt-3.5-turbo"
    print("✓ OpenAIClient setters work correctly")


def test_job_manager():
    """Test JobManager functionality"""
    print("\nTesting JobManager...")
    
    # Create a temporary job store
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = JobStore(storage_dir=tmpdir)
        manager = JobManager(job_store=store)
        
        # Test job creation
        job = manager.create_job("test_job", {"param": "value"})
        assert job["ok"] is True
        assert "job_id" in job
        assert job["state"] == "queued"
        print("✓ Job creation works")
        
        job_id = job["job_id"]
        
        # Test job status
        status = manager.get_job_status(job_id)
        assert status is not None
        assert status["ok"] is True
        assert status["job_id"] == job_id
        assert status["state"] == "queued"
        print("✓ Job status retrieval works")
        
        # Test job start
        success = manager.start_job(job_id)
        assert success is True
        status = manager.get_job_status(job_id)
        assert status["state"] == "running"
        assert status["started_at"] is not None
        print("✓ Job start works")
        
        # Test job completion
        success = manager.complete_job(job_id, success=True, result={"output": "done"})
        assert success is True
        status = manager.get_job_status(job_id)
        assert status["state"] == "succeeded"
        assert status["completed_at"] is not None
        print("✓ Job completion works")
        
        # Test job logs
        logs = manager.get_job_logs(job_id)
        assert logs is not None
        assert logs["ok"] is True
        assert len(logs["logs"]) > 0
        print("✓ Job logs retrieval works")
        
        # Test job cancellation
        job2 = manager.create_job("test_job_2", {})
        job2_id = job2["job_id"]
        success = manager.cancel_job(job2_id)
        assert success is True
        status = manager.get_job_status(job2_id)
        assert status["state"] == "canceled"
        print("✓ Job cancellation works")


def test_job_store():
    """Test JobStore functionality"""
    print("\nTesting JobStore...")
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = JobStore(storage_dir=tmpdir)
        
        # Test job creation
        job = store.create_job("req-123", "test_type", {"data": "test"})
        assert job is not None
        assert "job_id" in job
        assert job["job_type"] == "test_type"
        assert job["state"] == "queued"
        print("✓ JobStore creates jobs correctly")
        
        job_id = job["job_id"]
        
        # Test job retrieval
        retrieved = store.get_job(job_id)
        assert retrieved is not None
        assert retrieved["job_id"] == job_id
        print("✓ JobStore retrieves jobs correctly")
        
        # Test job update
        success = store.update_job(job_id, {"state": "running"})
        assert success is True
        updated = store.get_job(job_id)
        assert updated["state"] == "running"
        print("✓ JobStore updates jobs correctly")
        
        # Test log addition
        success = store.add_log(job_id, "Test log message", "info")
        assert success is True
        logs = store.get_logs(job_id)
        assert logs is not None
        assert len(logs) > 0
        assert logs[0]["message"] == "Test log message"
        print("✓ JobStore adds logs correctly")
        
        # Test list jobs
        job2 = store.create_job("req-124", "test_type_2", {})
        jobs = store.list_jobs()
        assert len(jobs) >= 2
        print("✓ JobStore lists jobs correctly")


def main():
    """Run all tests"""
    print("=" * 60)
    print("CIT v2.1 Component Tests")
    print("=" * 60)
    
    try:
        test_openai_client_init()
        test_job_manager()
        test_job_store()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
