#!/usr/bin/env python3
"""
Database Performance Benchmarking Suite
Comprehensive benchmarks for PostgreSQL, Redis, and Qdrant
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import statistics
import psycopg
import redis.asyncio as redis_async
from qdrant_client.async_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
PG_DATABASE = os.getenv("POSTGRES_DB", "xnai")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# Number of benchmark iterations
ITERATIONS = 100
WARM_UP = 10


class BenchmarkResult:
    """Container for benchmark results with statistical analysis"""

    def __init__(self, name: str, unit: str = "ms"):
        self.name = name
        self.unit = unit
        self.times: List[float] = []
        self.start_time = None

    def add_time(self, duration_ms: float):
        """Record a single measurement"""
        self.times.append(duration_ms)

    def stats(self) -> Dict[str, Any]:
        """Calculate statistical summary"""
        if not self.times:
            return {}
        
        sorted_times = sorted(self.times)
        n = len(sorted_times)
        
        return {
            "count": n,
            "mean": statistics.mean(sorted_times),
            "median": statistics.median(sorted_times),
            "stdev": statistics.stdev(sorted_times) if n > 1 else 0,
            "min": sorted_times[0],
            "max": sorted_times[-1],
            "p50": sorted_times[int(n * 0.50)],
            "p95": sorted_times[int(n * 0.95)],
            "p99": sorted_times[int(n * 0.99)],
            "unit": self.unit,
        }

    def __enter__(self):
        """Context manager entry - start timing"""
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        """Context manager exit - record time"""
        duration_ms = (time.time() - self.start_time) * 1000
        self.add_time(duration_ms)


class PostgreSQLBenchmark:
    """PostgreSQL performance benchmarks"""

    def __init__(self):
        self.conn: Optional[psycopg.AsyncConnection] = None
        self.results: Dict[str, BenchmarkResult] = {}

    async def connect(self):
        """Establish connection pool"""
        logger.info("Connecting to PostgreSQL...")
        self.conn = await psycopg.AsyncConnection.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DATABASE,
        )
        logger.info("PostgreSQL connected")

    async def disconnect(self):
        """Close connection"""
        if self.conn:
            await self.conn.close()

    async def setup(self):
        """Create test tables"""
        logger.info("Setting up PostgreSQL test data...")
        
        async with self.conn.cursor() as cur:
            # Create test table
            await cur.execute("""
                DROP TABLE IF EXISTS benchmark_test CASCADE;
                CREATE TABLE benchmark_test (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes
            await cur.execute("""
                CREATE INDEX idx_category ON benchmark_test(category);
                CREATE INDEX idx_created_at ON benchmark_test(created_at);
            """)
            
            await self.conn.commit()
            logger.info("PostgreSQL test table created")

    async def benchmark_select(self, rows: int = 100):
        """Benchmark SELECT queries"""
        logger.info(f"Benchmarking SELECT with {rows} rows...")
        
        # Insert test data
        async with self.conn.cursor() as cur:
            await cur.execute(f"""
                INSERT INTO benchmark_test (title, content, category)
                SELECT 'Title ' || n, 'Content ' || n, 'Category ' || (n % 5)
                FROM generate_series(1, {rows}) AS n
            """)
            await self.conn.commit()
        
        result = BenchmarkResult("SELECT", "ms")
        
        # Warm up
        async with self.conn.cursor() as cur:
            for _ in range(WARM_UP):
                await cur.execute("SELECT * FROM benchmark_test WHERE category = %s", ("Category 1",))
                await cur.fetchall()
        
        # Benchmark
        async with self.conn.cursor() as cur:
            for _ in range(ITERATIONS):
                with result:
                    await cur.execute("SELECT * FROM benchmark_test WHERE category = %s", ("Category 1",))
                    await cur.fetchall()
        
        self.results["SELECT"] = result
        logger.info(f"SELECT benchmark complete: {result.stats()}")

    async def benchmark_insert(self, rows: int = 100):
        """Benchmark INSERT operations"""
        logger.info(f"Benchmarking INSERT ({rows} rows)...")
        
        result = BenchmarkResult("INSERT", "ms")
        
        # Warm up
        async with self.conn.cursor() as cur:
            for _ in range(WARM_UP):
                await cur.execute(
                    "INSERT INTO benchmark_test (title, content, category) VALUES (%s, %s, %s)",
                    (f"Test {_}", f"Content {_}", "Category 1")
                )
                await self.conn.commit()
        
        # Benchmark
        async with self.conn.cursor() as cur:
            for i in range(ITERATIONS):
                with result:
                    await cur.execute(
                        "INSERT INTO benchmark_test (title, content, category) VALUES (%s, %s, %s)",
                        (f"Test {i}", f"Content {i}", "Category 1")
                    )
                    await self.conn.commit()
        
        self.results["INSERT"] = result
        logger.info(f"INSERT benchmark complete: {result.stats()}")

    async def benchmark_update(self):
        """Benchmark UPDATE operations"""
        logger.info("Benchmarking UPDATE...")
        
        result = BenchmarkResult("UPDATE", "ms")
        
        async with self.conn.cursor() as cur:
            # Warm up
            for _ in range(WARM_UP):
                await cur.execute(
                    "UPDATE benchmark_test SET content = %s WHERE id = %s",
                    (f"Updated {_}", 1)
                )
                await self.conn.commit()
            
            # Benchmark
            for i in range(ITERATIONS):
                with result:
                    await cur.execute(
                        "UPDATE benchmark_test SET content = %s WHERE id = %s",
                        (f"Updated {i}", (i % 50) + 1)
                    )
                    await self.conn.commit()
        
        self.results["UPDATE"] = result
        logger.info(f"UPDATE benchmark complete: {result.stats()}")

    async def benchmark_delete(self):
        """Benchmark DELETE operations"""
        logger.info("Benchmarking DELETE...")
        
        result = BenchmarkResult("DELETE", "ms")
        
        async with self.conn.cursor() as cur:
            # Warm up
            for _ in range(WARM_UP):
                await cur.execute("INSERT INTO benchmark_test (title, content, category) VALUES (%s, %s, %s)",
                                (f"ToDelete {_}", f"Content {_}", "DeleteMe"))
                await self.conn.commit()
            
            await cur.execute("SELECT id FROM benchmark_test WHERE category = %s", ("DeleteMe",))
            to_delete = await cur.fetchall()
            
            # Benchmark
            for i, (row_id,) in enumerate(to_delete[:ITERATIONS]):
                with result:
                    await cur.execute("DELETE FROM benchmark_test WHERE id = %s", (row_id,))
                    await self.conn.commit()
        
        self.results["DELETE"] = result
        logger.info(f"DELETE benchmark complete: {result.stats()}")

    async def benchmark_fts(self, doc_count: int = 1000):
        """Benchmark full-text search"""
        logger.info(f"Benchmarking FTS with {doc_count} documents...")
        
        async with self.conn.cursor() as cur:
            # Create FTS table
            await cur.execute("""
                DROP TABLE IF EXISTS benchmark_fts CASCADE;
                CREATE TABLE benchmark_fts (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL
                );
                CREATE INDEX idx_fts_content ON benchmark_fts USING GIN(to_tsvector('english', content));
            """)
            
            # Insert test data
            await cur.execute(f"""
                INSERT INTO benchmark_fts (content)
                SELECT 'Document ' || n || ' contains various keywords for testing full text search'
                FROM generate_series(1, {doc_count}) AS n
            """)
            await self.conn.commit()
        
        result = BenchmarkResult("FTS", "ms")
        
        # Warm up
        async with self.conn.cursor() as cur:
            for _ in range(WARM_UP):
                await cur.execute("""
                    SELECT * FROM benchmark_fts 
                    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', 'testing')
                """)
                await cur.fetchall()
        
        # Benchmark
        async with self.conn.cursor() as cur:
            for _ in range(ITERATIONS):
                with result:
                    await cur.execute("""
                        SELECT * FROM benchmark_fts 
                        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', 'testing')
                    """)
                    await cur.fetchall()
        
        self.results[f"FTS_{doc_count}"] = result
        logger.info(f"FTS_{doc_count} benchmark complete: {result.stats()}")

    async def benchmark_index_creation(self, table_size: int = 10000):
        """Benchmark index creation time"""
        logger.info(f"Benchmarking index creation on {table_size} rows...")
        
        async with self.conn.cursor() as cur:
            # Create test table with data
            await cur.execute(f"""
                DROP TABLE IF EXISTS benchmark_index_test CASCADE;
                CREATE TABLE benchmark_index_test (
                    id SERIAL PRIMARY KEY,
                    value_a VARCHAR(100),
                    value_b VARCHAR(100),
                    value_c VARCHAR(100)
                );
                INSERT INTO benchmark_index_test (value_a, value_b, value_c)
                SELECT 'A' || n, 'B' || n, 'C' || n
                FROM generate_series(1, {table_size}) AS n
            """)
            await self.conn.commit()
        
        result = BenchmarkResult("INDEX_CREATION", "ms")
        
        # Benchmark index creation
        async with self.conn.cursor() as cur:
            for i in range(5):  # Create 5 different indexes
                await cur.execute(f"DROP INDEX IF EXISTS idx_bench_{i} CASCADE")
                
                with result:
                    await cur.execute(f"CREATE INDEX idx_bench_{i} ON benchmark_index_test(value_{chr(97+i)})")
                
                await self.conn.commit()
        
        self.results["INDEX_CREATION"] = result
        logger.info(f"INDEX_CREATION benchmark complete: {result.stats()}")

    async def benchmark_connection_pool(self):
        """Benchmark connection creation time"""
        logger.info("Benchmarking connection creation...")
        
        result = BenchmarkResult("CONNECTION", "ms")
        
        for _ in range(ITERATIONS):
            with result:
                conn = await psycopg.AsyncConnection.connect(
                    host=PG_HOST,
                    port=PG_PORT,
                    user=PG_USER,
                    password=PG_PASSWORD,
                    dbname=PG_DATABASE,
                )
                await conn.close()
        
        self.results["CONNECTION"] = result
        logger.info(f"CONNECTION benchmark complete: {result.stats()}")

    async def run_all(self):
        """Run all PostgreSQL benchmarks"""
        await self.connect()
        try:
            await self.setup()
            await self.benchmark_connection_pool()
            await self.benchmark_select(100)
            await self.benchmark_insert(100)
            await self.benchmark_update()
            await self.benchmark_delete()
            await self.benchmark_fts(1000)
            await self.benchmark_fts(10000)
            await self.benchmark_index_creation(10000)
        finally:
            await self.disconnect()

    def get_results(self) -> Dict[str, Dict[str, Any]]:
        """Get all benchmark results"""
        return {
            name: result.stats() for name, result in self.results.items()
        }


class RedisBenchmark:
    """Redis performance benchmarks"""

    def __init__(self):
        self.client: Optional[redis_async.Redis] = None
        self.results: Dict[str, BenchmarkResult] = {}

    async def connect(self):
        """Establish connection"""
        logger.info("Connecting to Redis...")
        self.client = redis_async.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD if REDIS_PASSWORD else None,
            decode_responses=True,
        )
        await self.client.ping()
        logger.info("Redis connected")

    async def disconnect(self):
        """Close connection"""
        if self.client:
            await self.client.close()

    async def cleanup(self):
        """Clean up test data"""
        if self.client:
            await self.client.delete("bench:key", "bench:hash", "bench:list")

    async def benchmark_get(self):
        """Benchmark GET (cache hits)"""
        logger.info("Benchmarking GET...")
        
        # Set test data
        await self.client.set("bench:key", "test_value" * 10)
        
        result = BenchmarkResult("GET", "ms")
        
        # Warm up
        for _ in range(WARM_UP):
            await self.client.get("bench:key")
        
        # Benchmark
        for _ in range(ITERATIONS):
            with result:
                await self.client.get("bench:key")
        
        self.results["GET"] = result
        logger.info(f"GET benchmark complete: {result.stats()}")

    async def benchmark_set(self):
        """Benchmark SET operations"""
        logger.info("Benchmarking SET...")
        
        result = BenchmarkResult("SET", "ms")
        
        # Warm up
        for i in range(WARM_UP):
            await self.client.set(f"bench:warmup:{i}", f"value_{i}")
        
        # Benchmark
        for i in range(ITERATIONS):
            with result:
                await self.client.set(f"bench:key:{i}", f"value_{i}" * 10)
        
        self.results["SET"] = result
        logger.info(f"SET benchmark complete: {result.stats()}")

    async def benchmark_hgetall(self):
        """Benchmark HGETALL operations"""
        logger.info("Benchmarking HGETALL...")
        
        # Set test data (large hash)
        hash_data = {f"field_{i}": f"value_{i}" * 5 for i in range(100)}
        await self.client.hset("bench:hash", mapping=hash_data)
        
        result = BenchmarkResult("HGETALL", "ms")
        
        # Warm up
        for _ in range(WARM_UP):
            await self.client.hgetall("bench:hash")
        
        # Benchmark
        for _ in range(ITERATIONS):
            with result:
                await self.client.hgetall("bench:hash")
        
        self.results["HGETALL"] = result
        logger.info(f"HGETALL benchmark complete: {result.stats()}")

    async def benchmark_memory_per_document(self):
        """Benchmark memory consumption per cached document"""
        logger.info("Benchmarking memory consumption...")
        
        # Get initial memory
        info = await self.client.info("memory")
        initial_used = info["used_memory"]
        
        # Store 100 documents
        doc_size_bytes = 1000
        num_docs = 100
        for i in range(num_docs):
            doc = "x" * doc_size_bytes
            await self.client.set(f"bench:doc:{i}", doc)
        
        # Get final memory
        info = await self.client.info("memory")
        final_used = info["used_memory"]
        
        memory_per_doc = (final_used - initial_used) / num_docs
        
        self.results["MEMORY_PER_DOC"] = BenchmarkResult("MEMORY_PER_DOC", "bytes")
        self.results["MEMORY_PER_DOC"].times = [memory_per_doc]
        
        logger.info(f"Memory per document: {memory_per_doc:.2f} bytes")

    async def benchmark_eviction(self):
        """Benchmark eviction performance under memory pressure"""
        logger.info("Benchmarking eviction under pressure...")
        
        # Set memory limit
        await self.client.config_set("maxmemory", "100mb")
        await self.client.config_set("maxmemory-policy", "allkeys-lru")
        
        result = BenchmarkResult("EVICTION", "ms")
        
        # Fill up to trigger eviction
        try:
            for i in range(ITERATIONS):
                with result:
                    large_value = "x" * 100000
                    await self.client.set(f"bench:evict:{i}", large_value)
        except Exception as e:
            logger.warning(f"Eviction test encountered: {e}")
        
        self.results["EVICTION"] = result
        logger.info(f"EVICTION benchmark complete: {result.stats()}")

    async def run_all(self):
        """Run all Redis benchmarks"""
        await self.connect()
        try:
            await self.benchmark_get()
            await self.benchmark_set()
            await self.benchmark_hgetall()
            await self.benchmark_memory_per_document()
            await self.benchmark_eviction()
            await self.cleanup()
        finally:
            await self.disconnect()

    def get_results(self) -> Dict[str, Dict[str, Any]]:
        """Get all benchmark results"""
        return {
            name: result.stats() for name, result in self.results.items()
        }


class QdrantBenchmark:
    """Qdrant vector database benchmarks"""

    def __init__(self):
        self.client: Optional[AsyncQdrantClient] = None
        self.results: Dict[str, BenchmarkResult] = {}

    async def connect(self):
        """Establish connection"""
        logger.info("Connecting to Qdrant...")
        self.client = AsyncQdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            api_key=QDRANT_API_KEY if QDRANT_API_KEY else None,
        )
        logger.info("Qdrant connected")

    async def disconnect(self):
        """Close connection"""
        if self.client:
            await self.client.close()

    async def cleanup(self):
        """Clean up test collections"""
        if self.client:
            collections = ["bench_384", "bench_768", "bench_1152"]
            for coll in collections:
                try:
                    await self.client.delete_collection(coll)
                except:
                    pass

    async def benchmark_insert(self, vector_dim: int, num_vectors: int):
        """Benchmark vector insertion"""
        logger.info(f"Benchmarking insertion of {num_vectors} {vector_dim}-dim vectors...")
        
        collection_name = f"bench_{vector_dim}"
        
        # Create collection
        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
        )
        
        # Generate random vectors
        vectors = [np.random.randn(vector_dim).astype(np.float32).tolist() for _ in range(num_vectors)]
        
        result = BenchmarkResult("INSERT", "ms")
        
        # Benchmark insertion in batches
        batch_size = 100
        for batch_idx in range(0, num_vectors, batch_size):
            batch_end = min(batch_idx + batch_size, num_vectors)
            points = [
                PointStruct(
                    id=i,
                    vector=vectors[i],
                    payload={"idx": i}
                )
                for i in range(batch_idx, batch_end)
            ]
            
            with result:
                await self.client.upsert(
                    collection_name=collection_name,
                    points=points,
                )
        
        self.results[f"INSERT_{vector_dim}d"] = result
        logger.info(f"INSERT_{vector_dim}d benchmark complete: {result.stats()}")

    async def benchmark_search(self, vector_dim: int, num_vectors: int):
        """Benchmark vector search latency"""
        logger.info(f"Benchmarking search on {num_vectors} {vector_dim}-dim vectors...")
        
        collection_name = f"bench_{vector_dim}_search"
        
        # Create and populate collection
        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
        )
        
        vectors = [np.random.randn(vector_dim).astype(np.float32).tolist() for _ in range(num_vectors)]
        points = [
            PointStruct(
                id=i,
                vector=vectors[i],
                payload={"idx": i}
            )
            for i in range(num_vectors)
        ]
        
        await self.client.upsert(
            collection_name=collection_name,
            points=points,
        )
        
        # Wait for indexing
        await asyncio.sleep(1)
        
        result = BenchmarkResult("SEARCH", "ms")
        
        # Warm up
        query_vector = np.random.randn(vector_dim).astype(np.float32).tolist()
        for _ in range(WARM_UP):
            await self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=10,
            )
        
        # Benchmark
        for _ in range(ITERATIONS):
            query_vector = np.random.randn(vector_dim).astype(np.float32).tolist()
            with result:
                await self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=10,
                )
        
        self.results[f"SEARCH_{vector_dim}d"] = result
        logger.info(f"SEARCH_{vector_dim}d benchmark complete: {result.stats()}")

    async def run_all(self):
        """Run all Qdrant benchmarks"""
        await self.connect()
        try:
            await self.cleanup()
            
            # Benchmark different vector dimensions
            for dim in [384, 768, 1152]:
                await self.benchmark_insert(dim, 1000)
                await self.benchmark_search(dim, 1000)
            
            await self.cleanup()
        finally:
            await self.disconnect()

    def get_results(self) -> Dict[str, Dict[str, Any]]:
        """Get all benchmark results"""
        return {
            name: result.stats() for name, result in self.results.items()
        }


async def run_benchmarks():
    """Run all database benchmarks"""
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "PostgreSQL": {},
        "Redis": {},
        "Qdrant": {},
    }
    
    # PostgreSQL benchmarks
    logger.info("=" * 60)
    logger.info("POSTGRESQL BENCHMARKS")
    logger.info("=" * 60)
    pg_bench = PostgreSQLBenchmark()
    await pg_bench.run_all()
    all_results["PostgreSQL"] = pg_bench.get_results()
    
    # Redis benchmarks
    logger.info("\n" + "=" * 60)
    logger.info("REDIS BENCHMARKS")
    logger.info("=" * 60)
    redis_bench = RedisBenchmark()
    await redis_bench.run_all()
    all_results["Redis"] = redis_bench.get_results()
    
    # Qdrant benchmarks
    logger.info("\n" + "=" * 60)
    logger.info("QDRANT BENCHMARKS")
    logger.info("=" * 60)
    qdrant_bench = QdrantBenchmark()
    await qdrant_bench.run_all()
    all_results["Qdrant"] = qdrant_bench.get_results()
    
    # Save results
    output_file = Path("benchmarks/database_benchmark_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"\nResults saved to {output_file}")
    
    return all_results


if __name__ == "__main__":
    results = asyncio.run(run_benchmarks())
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("BENCHMARK SUMMARY")
    logger.info("=" * 60)
    
    for system, benchmarks in results.items():
        if system == "timestamp":
            continue
        logger.info(f"\n{system}:")
        for name, stats in benchmarks.items():
            if stats:
                logger.info(
                    f"  {name}: p50={stats.get('p50', 0):.2f}ms, "
                    f"p95={stats.get('p95', 0):.2f}ms, "
                    f"p99={stats.get('p99', 0):.2f}ms"
                )
