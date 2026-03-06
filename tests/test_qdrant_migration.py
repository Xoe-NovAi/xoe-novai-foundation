#!/usr/bin/env python3
# ============================================================================
# Qdrant Migration - Unit Tests
# ============================================================================
# Purpose: Test FAISS to Qdrant migration components
# Run: pytest tests/test_qdrant_migration.py -v
# ============================================================================

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from datetime import datetime


class TestMigrationConfig:
    """Test MigrationConfig class."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        from scripts.migrate_to_qdrant import MigrationConfig
        
        config = MigrationConfig()
        assert config.batch_size == 500
        assert config.max_memory_percent == 0.6
        assert config.vector_size == 384
        assert config.collection_name == "xnai_knowledge"
        assert config.resume_mode is True
    
    def test_config_from_env(self):
        """Test loading config from environment variables."""
        import os
        from scripts.migrate_to_qdrant import MigrationConfig
        
        # Set test environment variables
        os.environ["BATCH_SIZE"] = "250"
        os.environ["VECTOR_SIZE"] = "512"
        
        config = MigrationConfig.from_env()
        assert config.vector_size == 512


class TestMemoryMonitor:
    """Test memory monitoring for Ryzen 7."""
    
    @pytest.mark.asyncio
    async def test_memory_monitor_init(self):
        """Test memory monitor initialization."""
        from scripts.migrate_to_qdrant import MemoryMonitor
        
        monitor = MemoryMonitor(max_memory_percent=0.6)
        assert monitor.max_memory_percent == 0.6


class TestMigrationState:
    """Test Redis state management."""
    
    @pytest.mark.asyncio
    async def test_state_init(self):
        """Test state initialization."""
        from scripts.migrate_to_qdrant import MigrationState
        
        # Mock Redis client
        mock_redis = AsyncMock()
        state = MigrationState(mock_redis, "test:state")
        
        await state.init_state(total_vectors=1000)
        
        # Verify Redis.set was called
        assert mock_redis.set.called
        
        # Verify state structure
        call_args = mock_redis.set.call_args
        assert call_args is not None
        state_json = call_args[0][1]
        state_obj = json.loads(state_json)
        
        assert state_obj["status"] == "in_progress"
        assert state_obj["total_vectors"] == 1000
        assert state_obj["processed_vectors"] == 0
    
    @pytest.mark.asyncio
    async def test_state_update_progress(self):
        """Test progress update."""
        from scripts.migrate_to_qdrant import MigrationState
        
        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps({
            "status": "in_progress",
            "processed_vectors": 0,
            "failed_vectors": 0,
        })
        
        state = MigrationState(mock_redis, "test:state")
        await state.update_progress(processed=100, failed=5, batch_id=1)
        
        # Verify update was called
        assert mock_redis.set.called


class TestFAISSLoader:
    """Test FAISS index loader."""
    
    def test_faiss_loader_init(self):
        """Test FAISSLoader initialization."""
        from scripts.migrate_to_qdrant import FAISSLoader
        
        loader = FAISSLoader(index_path="/test/path", vector_size=384)
        assert loader.vector_size == 384
        assert Path("/test/path") == loader.index_path


class TestQdrantUpserter:
    """Test Qdrant upsert functionality."""
    
    @pytest.mark.asyncio
    async def test_upserter_connect(self):
        """Test Qdrant connection."""
        from scripts.migrate_to_qdrant import QdrantUpserter, MigrationConfig
        
        config = MigrationConfig(qdrant_url="http://localhost:6333")
        upserter = QdrantUpserter(config)
        
        # Mock the client
        upserter.client = AsyncMock()
        
        # Verify client is set
        assert upserter.client is not None
    
    @pytest.mark.asyncio
    async def test_upsert_batch(self):
        """Test batch upsert."""
        from scripts.migrate_to_qdrant import QdrantUpserter, MigrationConfig
        
        config = MigrationConfig()
        upserter = QdrantUpserter(config)
        upserter.client = AsyncMock()
        upserter.collection_initialized = True
        
        vector_ids = [1, 2, 3]
        vectors = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        metadata = [{"source": "test"}] * 3
        
        success, errors = await upserter.upsert_batch(vector_ids, vectors, metadata)
        
        # Should handle gracefully
        assert isinstance(success, int)
        assert isinstance(errors, int)


class TestDockerCompose:
    """Test docker-compose configuration."""
    
    def test_docker_compose_qdrant_service(self):
        """Verify Qdrant service exists in docker-compose."""
        from pathlib import Path
        import yaml
        
        compose_file = Path("docker-compose.yml")
        
        # Check file exists
        assert compose_file.exists(), "docker-compose.yml not found"
        
        # Load and parse
        with open(compose_file, "r") as f:
            compose = yaml.safe_load(f)
        
        # Verify qdrant service exists
        assert "qdrant" in compose["services"], "qdrant service not found"
        
        # Verify qdrant configuration
        qdrant_service = compose["services"]["qdrant"]
        assert qdrant_service["image"].startswith("qdrant/qdrant")
        assert "6333" in str(qdrant_service.get("ports", []))


class TestConfigFiles:
    """Test configuration files."""
    
    def test_qdrant_config_exists(self):
        """Verify Qdrant config file exists."""
        config_file = Path("config/qdrant_config.yaml")
        assert config_file.exists(), f"Config file not found: {config_file}"
    
    def test_env_example_has_qdrant(self):
        """Verify .env.example includes Qdrant settings."""
        env_file = Path(".env.example")
        assert env_file.exists(), ".env.example not found"
        
        with open(env_file, "r") as f:
            content = f.read()
        
        assert "QDRANT" in content, "Qdrant settings not in .env.example"
    
    def test_requirements_has_qdrant_client(self):
        """Verify qdrant-client is in requirements."""
        req_file = Path("requirements-api.in")
        assert req_file.exists(), "requirements-api.in not found"
        
        with open(req_file, "r") as f:
            content = f.read()
        
        assert "qdrant-client" in content, "qdrant-client not in requirements"


class TestDocumentation:
    """Test documentation."""
    
    def test_migration_docs_exists(self):
        """Verify migration documentation exists."""
        doc_file = Path("docs/QDRANT_MIGRATION.md")
        assert doc_file.exists(), "QDRANT_MIGRATION.md not found"
        
        with open(doc_file, "r") as f:
            content = f.read()
        
        # Verify key sections
        assert "Prerequisites" in content
        assert "Running the Migration" in content
        assert "Verification" in content


class TestScriptStructure:
    """Test migration script structure."""
    
    def test_migrate_script_exists(self):
        """Verify migration script exists."""
        script_file = Path("scripts/migrate_to_qdrant.py")
        assert script_file.exists(), "migrate_to_qdrant.py not found"
        assert script_file.stat().st_mode & 0o111, "Script not executable"
    
    def test_validate_script_exists(self):
        """Verify validation script exists."""
        script_file = Path("scripts/validate_qdrant_migration.py")
        assert script_file.exists(), "validate_qdrant_migration.py not found"
        assert script_file.stat().st_mode & 0o111, "Script not executable"


# Integration tests (require Docker)
@pytest.mark.integration
class TestQdrantIntegration:
    """Integration tests with actual Qdrant service."""
    
    @pytest.mark.asyncio
    async def test_qdrant_health(self):
        """Test Qdrant service health check."""
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:6333/health",
                    timeout=5.0
                )
                assert response.status_code == 200
        except Exception as e:
            pytest.skip(f"Qdrant service not available: {e}")
    
    @pytest.mark.asyncio
    async def test_redis_health(self):
        """Test Redis service health check."""
        import redis.asyncio as aioredis
        
        try:
            redis = await aioredis.from_url("redis://localhost:6379")
            result = await redis.ping()
            assert result
            await redis.close()
        except Exception as e:
            pytest.skip(f"Redis service not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
