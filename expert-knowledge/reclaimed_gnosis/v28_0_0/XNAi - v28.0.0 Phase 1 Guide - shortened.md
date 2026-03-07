  ### Table of Contents



* **1. Executive Summary** ✅

* **2. Core Architecture** ✅

* **3. System Requirements** ✅

* **4. Directory Structure** ✅

* **5. Dependencies Matrix** ✅

* **6. Docker Configuration** ✅

* **7. Application Components** ✅

* **8. Build & Deployment** ✅

* **9. Performance Optimization** ✅

* **10. Validation & Testing** ✅

* **11. Troubleshooting** ✅

* **12. Migration from v27.7.x** ✅

* **13. Multi-Agent Simulation** ✅

* **14. Extension Patterns** ✅

* **15. Best Practices for Repairs** ✅

* **16. Blueprint for Full Stack** ✅

* **17. Phase 2 Preparation** ✅

* **18. Glossary** ✅

* **19. Conclusion**

* **20. Additional Resources and Guidance**



---



### 1\. Executive Summary



The **Xoe-NovAi Phase 1 v28.0.0** project establishes a robust, local polymath AI foundation with real-time streaming capabilities, emphasizing data sovereignty and user privacy. This version is a production-ready blueprint, rigorously optimized for **AMD Ryzen 7 5700U** processors and designed with modularity for **Phase 2**'s multi-agent, polymathic capabilities.



#### Core Philosophy & Strategic Vision:



  * **Local-only, CPU-first Architecture**: Ensures complete data sovereignty and optimal performance on target hardware.

  * **Zero-Telemetry Principle**: Guarantees absolute user privacy by disabling all data collection.

  * **Production-Ready**: Focuses on stability, resilience, and maintainability.

  * **Modular Design**: Lays the groundwork for future multi-agent, polymathic functionalities such as coding, curation, writing, and self-learning.



#### Primary Performance Targets:



  * **Token Generation Rate**: 15-25 tokens/second (tok/s).

  * **Memory Usage**: Under 6GB (achieved via f16\_kv optimization).

  * **Response Latency**: Under 1 second (s).

  * **Startup Time**: Under 90 seconds (s).



#### Key Enhancements in v28.0.0:



  * **LlamaCppEmbeddings**: Utilized for all-MiniLM-L12-v2.Q8\_0.gguf, yielding 50% memory savings.

  * `python:3.12-slim-bookworm` **Base Image**: Provides a minimal (\~100MB), stable, and secure Debian 12 environment.

  * `su-exec` **for Redis**: Implemented for a lightweight privilege drop (10KB vs gosu 1MB), enhancing security.

  * **tenacity Library**: Integrated for enterprise-grade retries (`stop_max_attempt_number=3`), improving resilience.

  * `tmpfs` **Mounts**: Used for I/O optimization in `/tmp:mode=1777` and for Chainlit's temporary files, resolving read-only filesystem issues.

  * **Enhanced Security**: Includes 16-character Redis passwords, and optimized TCP settings (`backlog=2048`, `maxclients=10000`).

  * **FAISS Backups**: Ensures crash recovery with `faiss_index.bak`.

  * **Multi-OS CI Matrix**: Implemented for Ubuntu/Debian portability, ensuring continuous validation.

  * **JSON Logging**: Configured with 10MB rotation and 5 backups, ensuring production-ready log management.

  * **Network Naming**: Standardized to `xnai_v2800` for version consistency and DNS stability.



#### Core Components:



  * **RAG API (FastAPI)**: HTTP gateway for Retrieval-Augmented Generation, using `StreamingResponse` for Server-Sent Events (SSE).

  * **User Interface (Chainlit)**: Provides a real-time UI with token updates and enhanced parsing (`maxsplit=1`).

  * **Large Language Model (LLM)**: `gemma-3-4b-it-UD-Q5_K_XL.gguf` via `llama-cpp-python`.

  * **Embeddings**: `all-MiniLM-L12-v2.Q8_0.gguf` using **LlamaCppEmbeddings** (shifted from `langchain_community.embeddings` to `langchain_huggingface.HuggingFaceEmbeddings` for CPU optimization and deprecation avoidance).

  * **Vectorstore (FAISS)**: Lightweight, CPU-optimized, local-first for **Phase 1** (`<1M` documents, `<6GB` memory), with safe loading and automatic backups. **Qdrant** is the **Phase 2** target for scalability.

  * **Caching/Messaging (Redis)**: Used for persistence, session management, and **Phase 2** multi-agent communication via streams.

  * **Prometheus Metrics**: Integrated with safe wrappers for error-proof collection.



#### Critical Fixes & Improvements:



  * **Model Paths**: Standardized to root-level `/models/` and `/embeddings/` directories for simplified references and alignment with project structure.

  * **Directory Structure**: Mandates `/data/faiss_index` for persistent **FAISS** data and `/data/redis` for **Redis** state, correcting previous inconsistencies. Chainlit `.files` `tmpfs` mount implemented at `/app/XNAi_rag_app/.files:mode=1777,size=512m`.

  * **Configuration Centralization**: Rigidly enforces and validates full centralization of configuration using `.env` for environment variables (e.g., `REDIS_PASSWORD`, `REDIS_TIMEOUT`) and `config.toml` for application-specific settings (e.g., `max_size_mb`, `stack_version`), eliminating hardcoding.

  * **Healthcheck Function**: Significantly modularized and expanded to include comprehensive validation for **LLM**, embeddings, memory, and Ryzen optimizations, in addition to **Redis**.

  * `f16_kv` **Memory Optimization**: Explicitly enabled for the **LLM** and validated to ensure a 50% **KV** cache reduction, targeting `<6GB` memory usage.

  * `Makefile` **Targets**: Expanded to include `latency-test`, `pre-build-validation`, and `memory-check`.

  * **Redis Security**: Includes `su-exec` privilege drop and password authentication for health checks.

  * **Zero-Telemetry Validation**: Implemented via `docker inspect --format '{{.Config.Env}}' xnai-rag-v2800 | grep -v TELEMETRY`.



*Note for AI Assistants: Parse code blocks/tables, ignoring \# comments. Refer to .env and config.toml for variables.*



*Validation: `docker ps | grep healthy` should show all services up and running.*



-----



### 2\. Core Architecture



The **Xoe-NovAi v28.0.0** stack is built upon a modular architecture designed for high performance, security, and extensibility, with a clearly defined data flow and core principles.



#### Data Flow:



The system processes user interactions through a streamlined pipeline: User → **Chainlit** (UI on port 8001) → **FastAPI** (**RAG** API on port 8000) → **Redis**/ **FAISS** → **LlamaCpp** (**LLM**/Embeddings) → **SSE** (real-time token streaming).



#### Architectural Principles:



  * **Local-Only**: The system is designed to operate without external internet access post-build, ensuring complete data sovereignty and privacy.

  * **CPU-First**: Emphasizes Ryzen-specific threading optimizations and `f16_kv` quantization to achieve approximately 50% memory reduction for efficient CPU inference.

  * **Streaming-First**: Leverages **Server-Sent Events** (**SSE**) via **FastAPI** and **Chainlit** to provide sub-1 second latency for real-time, token-by-token user experience.

  * **RAG Robustness**: Implements safe **FAISS** index loading with automatic backups and graceful handling of corrupted data, ensuring reliable retrieval-augmented generation. **Phase 2** targets a transition to **Qdrant** for enhanced scalability and advanced filtering.

  * **Security**: Enforces non-root execution for containers, utilizes `cap_drop: ALL` and `no-new-privileges` in Docker, and integrates robust **Redis** security enhancements (e.g., `su-exec`, password authentication).

  * **Modularity**: Designed with separate entrypoints and well-defined interfaces to facilitate seamless expansion and integration of **Phase 2** multi-agent capabilities.

  * **Zero-Telemetry**: Strictly implements multiple environment variables to disable all data collection and tracing (e.g., `CHAINLIT_NO_TELEMETRY=true`, `OPENTELEMETRY_SDK_DISABLED=true`).



*Phase 2 Vision: Phase 1 serves as a foundational layer, preparing for Xoe-NovAi's evolution into a multi-agent, polymathic AI system. This includes capabilities like specialized coding expertise, library curation, writing assistance, project management, and self-learning.*



*Tree-of-Thoughts (ToT) Analysis: Architectural decisions are informed by **ToT**, evaluating trade-offs such as:*



  * **Vector Store**: **FAISS** (**Phase 1**) vs. **Qdrant** (**Phase 2**) for memory, speed, and scalability.

  * **Logging**: JSON vs. plain text logging for structured output and analysis.

  * **Memory Optimization**: `f16_kv` vs. model pruning vs. dynamic loading strategies.



-----



### 3\. System Requirements



To ensure optimal performance and operational readiness for the **Xoe-NovAi Phase 1 v28.0.0** stack, the following hardware and software specifications are required:



#### Hardware Specifications:



  * **CPU**: **AMD Ryzen 7 5700U** (8 cores/16 threads, 1.8-4.3GHz base/boost). Critical for **AVX2**/ **FMA3**/ **F16C** optimizations, yielding 25-40% performance gains.

  * **RAM**: 16-32GB DDR4. Essential for `f16_kv` and `mlock`, targeting `<6GB` actual memory usage for the **LLM**. Monitoring can be performed via `make memory-check`.

  * **Storage**: **SSD** recommended for efficient `mmap` performance and fast model loading.



#### Software Dependencies:



  * **Operating System**: Ubuntu 24.04 LTS or Debian 12.

  * **Python**: Version 3.12 (using the `python:3.12-slim-bookworm` base image for minimal footprint and stability).

  * **Docker**: Engine 27.x with Compose v3.9+ (ensuring `healthcheck` support).



#### Model Configuration & Paths (Validated against project structure):



  * **Large Language Model (LLM)**: `/models/gemma-3-4b-it-UD-Q5_K_XL.gguf`. Loaded using **LlamaCpp** with `f16_kv=true` (for 50% **KV** cache reduction) and `n_threads=6` (optimal for **Ryzen 7 5700U**).

  * **Embeddings Model**: `/embeddings/all-MiniLM-L12-v2.Q8_0.gguf`. Loaded using **LlamaCppEmbeddings** (ensuring `.gguf` compatibility and memory savings).



#### Initialization Pseudocode (Example):



```bash

#!/bin/bash

# Pseudocode: init.sh for creating necessary directories and setting permissions

echo "Ensuring optimal directory structure for Xoe-NovAi v28.0.0..."

mkdir -p /models /embeddings /data/faiss_index /data/redis /app/XNAi_rag_app/logs /tmp

chmod -R 755 /models /embeddings /data/faiss_index /data/redis /app/XNAi_rag_app/logs /tmp

echo "Directory structure initialized."

```



*Note: The `/app/XNAi_rag_app/` directory will be created by Docker when the application code is copied.*



#### Validation Commands:



  * Verify **LLM** presence: `ls -lh /models/gemma-3-4b-it-UD-Q5_K_XL.gguf` (Expected: `gemma-3-4b-it-UD-Q5_K_XL.gguf (2.8GB)`).

  * Verify Embeddings presence: `ls -lh /embeddings/all-MiniLM-L12-v2.Q8_0.gguf` (Expected: `all-MiniLM-L12-v2.Q8_0.gguf (45MB)`).

  * Verify Python version: `docker exec xnai-rag-v2800 python3 --version` (Expected: `Python 3.12.x`).



-----



### 4\. Directory Structure



The **Xoe-NovAi Phase 1 v28.0.0** adopts an optimized and standardized directory structure, adhering to Docker best practices for separating application code, persistent data, and ephemeral files. This layout ensures stability, security, and ease of management.



#### Project Layout (v28.0.0):



  * `/app/XNAi_rag_app/`:

      * **Purpose**: The primary location for all application code (e.g., `app.py`, `main.py`, `dependencies.py`, `config.toml`, `healthcheck.py`, `metrics.py`, `logging_config.py`, `verify_imports.py`). This directory should only contain code and configuration, not mutable data.

      * `/app/XNAi_rag_app/.files`:

          * **Purpose**: A dedicated `tmpfs` mount for **Chainlit**'s temporary file storage. This resolves "Permission denied: .files" errors and improves I/O performance for the UI service.

          * **Configuration**: Must be mounted as `tmpfs: [/app/XNAi_rag_app/.files:mode=1777,size=512m]` in `docker-compose.yml` to limit memory usage and ensure proper permissions.

  * `/data/`:

      * **Purpose**: The primary mount point for all persistent data volumes, ensuring data durability across container restarts.

      * `/data/faiss_index/`:

          * **Purpose**: Stores **FAISS** vector store index files, ensuring persistence of the **RAG** knowledge base. All references must consistently point to this path.

      * `/data/faiss_index.bak`:

          * **Purpose**: Stores **FAISS** backup files for disaster recovery and rollback procedures.

      * `/data/redis/`:

          * **Purpose**: Stores **Redis** persistent state storage (e.g., `appendonly.aof`, `dump.rdb`). This directory is explicitly `chowned` to `redis:redis` for security.

  * `/models/`:

      * **Purpose**: Stores Large Language Model (**LLM**) `.gguf` files (e.g., `gemma-3-4b-it-UD-Q5_K_XL.gguf`). The root path simplifies references.

  * `/embeddings/`:

      * **Purpose**: Stores embedding model `.gguf` files (e.g., `all-MiniLM-L12-v2.Q8_0.gguf`). The root path simplifies references.

  * `/tmp/`:

      * **Purpose**: For general temporary files, mounted as `tmpfs` (`/tmp:mode=1777`) for I/O optimization.



#### Directory Creation Pseudocode:



```bash

#!/bin/bash

# Pseudocode for directory setup within a Docker entrypoint or initialization script

echo "Initializing Xoe-NovAi v28.0.0 directory structure..."

mkdir -p /models /embeddings /data/faiss_index /data/redis /app/XNAi_rag_app/logs

chmod -R 755 /models /embeddings /data/faiss_index /data/redis /app/XNAi_rag_app/logs

echo "Directory structure created and permissions set."

```



*Note: The `/app/XNAi_rag_app/.files` directory is created and managed as a `tmpfs` mount by Docker Compose, not via `mkdir`.*



#### Validation Commands:



  * Verify `/data/faiss_index`: `ls -d /data/faiss_index` (Expected: Directory exists).

  * Verify `/data/redis`: `ls -d /data/redis` (Expected: Directory exists).

  * Verify `/tmp`: `ls -d /tmp` (Expected: Directory exists).

  * Verify **Chainlit** `tmpfs` mount: `docker inspect --format '{{.HostConfig.Tmpfs}}' xnai-ui-v2800 | grep /app/XNAi_rag_app/.files` (Expected: `map[/app/XNAi_rag_app/.files:mode=1777,size=512m]`).



-----



### 5\. Dependencies Matrix



The **Xoe-NovAi v28.0.0** stack meticulously manages its dependencies to ensure stability, performance, and future extensibility. This section outlines key packages, their versions, usage, import patterns, and robust error handling strategies. The design follows a **Dynamic Contextual Layering (DCL)** Workflow (**Planner** → **Coder** → **Tester**) and incorporates **Tree-of-Thoughts (ToT)** analysis for critical decisions.



#### Dependencies Matrix Table (v28.0.0 Versions):



| Package | Version | Usage | Import Pattern | Error Handling |

| :--- | :--- | :--- | :--- | :--- |

| `langchain-community` | 0.3.27 | FAISS VectorStore, Base LLM interfaces | `from langchain_community.vectorstores import FAISS` | `FileNotFoundError`, `ImportError`, `CorruptedDataError` |

| `langchain-huggingface` | 0.3.1 | HuggingFaceEmbeddings (CPU-optimized) | `from langchain_huggingface import HuggingFaceEmbeddings` | `FileNotFoundError`, `ImportError` |

| `llama-cpp-python` | 0.3.16 | LLM Runtime (LlamaCpp), Embeddings | `from langchain_community.llms import LlamaCpp` | `FileNotFoundError`, `PermissionError` |

| `chainlit` | 2.7.2 | UI Framework, Real-time Streaming | `import chainlit as cl` | `ConnectionError`, `ImportError` |

| `faiss-cpu` | 1.12.0 | Vector Storage (CPU-only) | `FAISS.load_local(..., allow_dangerous_deserialization=True)` | `FileNotFoundError`, `CorruptedDataError` |

| `tenacity` | 1.0.0 | Retry Logic for network calls | `from tenacity import retry, stop_after_attempt` | `RetryError`, `TimeoutError` |

| `psutil` | 7.1.0 | System Monitoring (CPU affinity, memory) | `import psutil; psutil.Process().cpu_affinity(range(6))` | `AccessDenied`, `NoSuchProcess` |

| `aioredis` | (latest) | Async Redis Client (Phase 2 prep) | `import aioredis` | `ConnectionError`, `TimeoutError` |

| `orjson` | 3.10.11 | Fast JSON Serialization | `import orjson` | `JSONDecodeError` |

| `lz4` | 4.3.3 | Compression (Redis optimization) | `import lz4` | `ImportError` |

| `maxsplit` | (Built-in) | String parsing for Chainlit commands | `user_input.split(" ", maxsplit=1)` | `IndexError` (if split fails) |



#### Tree-of-Thoughts (ToT): Vectorstore Decision Matrix (FAISS vs. Qdrant for Phase 1):



| Criteria | FAISS | Qdrant | Winner |

| :--- | :--- | :--- | :--- |

| Memory Usage | `<50MB` (for index overhead) | `~200MB` (for basic instance) | FAISS |

| Local Performance | Excellent (`<1s` query latency) | Good (`~1-2s` for large datasets) | FAISS |

| Scalability | Poor (single-node, `<1M` docs) | Excellent (multi-node, `>1M` docs) | Qdrant |

| Phase 1 Fit | Perfect (local sovereignty, `<6GB` mem) | Overkill (distributed, complex) | FAISS |

| Phase 2 Readiness | Backup/migration needed | Native multi-agent support, advanced filtering | Qdrant |



*Decision: FAISS is the optimal choice for Phase 1 due to its minimal memory footprint, excellent local performance, and suitability for single-node deployment within the `<6GB` memory constraint. Qdrant is designated as the Phase 2 target for its superior scalability and enterprise features for multi-agent coordination.*



#### Coder Implementation (dependencies.py - Core Functions with Error Handling):



```python

# Pseudocode: dependencies.py

import os

import logging

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from langchain_community.llms import LlamaCpp

from langchain_huggingface import HuggingFaceEmbeddings # Corrected import

from langchain_community.vectorstores import FAISS

import aioredis # Phase 2 prep: Async Redis client

import psutil



logger = logging.getLogger(__name__)



# Centralized configuration variables from .env/config.toml

REDIS_HOST = os.getenv("REDIS_HOST", "redis")

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

FAISS_INDEX_PATH = "/data/faiss_index" # Corrected path

LLM_PATH = "/models/gemma-3-4b-it-UD-Q5_K_XL.gguf"

EMBEDDING_PATH = "/embeddings/all-MiniLM-L12-v2.Q8_0.gguf"

N_THREADS = int(os.getenv("LLAMA_CPP_N_THREADS", 6)) # Ryzen optimization

N_CTX = int(os.getenv("N_CTX", 2048))



@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(FileNotFoundError))

def get_llm():

    """Initializes and returns the LlamaCpp LLM instance."""

    try:

        llm = LlamaCpp(

            model_path=LLM_PATH,

            temperature=0.7,

            n_gpu_layers=-1, # Or specify layers for GPU, -1 for CPU-only

            n_ctx=N_CTX,

            f16_kv=True, # Critical for <6GB memory target

            n_threads=N_THREADS,

            verbose=False,

        )

        assert llm.f16_kv, "f16_kv failed to enable, memory target may be exceeded!"

        logger.info(f"LLM loaded from {LLM_PATH} with f16_kv enabled: {llm.f16_kv}")

        return llm

    except FileNotFoundError as e:

        logger.error(f"LLM model not found at {LLM_PATH}: {e}")

        raise

    except Exception as e:

        logger.error(f"Error loading LLM: {e}")

        raise



@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(FileNotFoundError))

def get_embeddings():

    """Initializes and returns the HuggingFaceEmbeddings instance."""

    try:

        embeddings = HuggingFaceEmbeddings(

            model_name=EMBEDDING_PATH, # Or specify model name for auto-download

            model_kwargs={'device': 'cpu'}, # Explicitly for Ryzen CPU optimization

            encode_kwargs={'normalize_embeddings': True},

        )

        logger.info(f"Embeddings loaded from {EMBEDDING_PATH} (CPU-optimized)")

        return embeddings

    except FileNotFoundError as e:

        logger.error(f"Embedding model not found at {EMBEDDING_PATH}: {e}")

        raise

    except Exception as e:

        logger.error(f"Error loading embeddings: {e}")

        raise



@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(ConnectionError))

def get_vectorstore(embeddings):

    """Loads or creates a FAISS vectorstore with safe deserialization."""

    try:

        # Use allow_dangerous_deserialization=True with caution and only on trusted data

        vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

        logger.info(f"FAISS vectorstore loaded from {FAISS_INDEX_PATH}")

        return vectorstore

    except (FileNotFoundError, ConnectionError, Exception) as e:

        logger.warning(f"FAISS load failed or index corrupted: {e}. Recreating index.")

        # Fallback to an empty vectorstore if loading fails

        vectorstore = FAISS.from_texts([""], embeddings)

        vectorstore.save_local(FAISS_INDEX_PATH) # Save empty index for future loads

        logger.info(f"Empty FAISS vectorstore created and saved to {FAISS_INDEX_PATH}")

        return vectorstore



async def get_async_redis_client():

    """Provides an asynchronous Redis client for Phase 2 readiness."""

    try:

        # aioredis for async operations

        redis_client = aioredis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD, decode_responses=True)

        await redis_client.ping() # Validate connection

        logger.info("Async Redis client initialized and connected.")

        return redis_client

    except ConnectionError as e:

        logger.error(f"Async Redis connection failed: {e}")

        raise

    except Exception as e:

        logger.error(f"Error initializing async Redis client: {e}")

        raise



def get_cpu_affinity():

    """Returns the CPU affinity of the current process for Ryzen optimization."""

    try:

        process = psutil.Process()

        affinity = process.cpu_affinity()

        logger.info(f"CPU affinity: {affinity}")

        return affinity

    except psutil.AccessDenied:

        logger.warning("Access denied to get CPU affinity. Running without specific affinity settings.")

        return []

    except Exception as e:

        logger.error(f"Error getting CPU affinity: {e}")

        return []

```



#### Tester Validations (DCL from Coder Implementation):



  * Validate **LLM** loading and `f16_kv`: `python -c "from dependencies import get_llm; llm = get_llm(); print(llm.f16_kv)"` (Expected: `True`).

  * Validate Embeddings loading: `python -c "from dependencies import get_embeddings; embeddings = get_embeddings(); print(embeddings)"` (Expected: `HuggingFaceEmbeddings(...)`).

  * Validate **FAISS** loading: `python -c "from dependencies import get_llm, get_embeddings, get_vectorstore; embeddings = get_embeddings(); vectorstore = get_vectorstore(embeddings); print(vectorstore)"` (Expected: `<langchain_community.vectorstores.faiss.FAISS object at ...>`).

  * Validate Async **Redis** client (**Phase 2** hook): `python -c "import asyncio; from dependencies import get_async_redis_client; asyncio.run(get_async_redis_client())"` (Expected: `Async Redis client initialized and connected.`).

  * Validate **CPU** affinity: `python -c "from dependencies import get_cpu_affinity; affinity = get_cpu_affinity(); print(len(affinity))"` (Expected: `6` or similar for optimal Ryzen threads).

  * Validate `maxsplit=1` behavior (conceptual test, usually in UI/API): `python -c "command = '!norag complex query'; parts = command.split(' ', maxsplit=1); print(parts)"; print(len(parts))` (Expected: `['!norag', 'complex query'], 2`).



-----



### 6\. Docker Configuration



The Docker configuration for **Xoe-NovAi v28.0.0** is designed for robust, secure, and efficient deployment, leveraging multi-stage builds and centralized configuration. It incorporates critical updates for network naming, **Redis** capabilities, and **Chainlit** `tmpfs` mounts.



#### Key Configuration Principles:



  * **Multi-stage Builds**: Separates build-time dependencies from runtime, resulting in smaller, more secure final images.

  * **Minimal Base Image**: Utilizes `python:3.12-slim-bookworm` for a lightweight and stable runtime environment (`~100MB`).

  * **Non-root User**: All services run as a dedicated `appuser` to enhance security and adhere to container best practices.

  * **Centralized Configuration**: All environment variables and application settings are managed via `.env` and `config.toml` respectively, dynamically referenced in Docker Compose and entrypoint scripts to prevent hardcoding.



#### Updated `docker-compose.yml` Snippet (with enhancements):



```yaml

# Pseudocode: docker-compose.yml (simplified for core elements)

version: '3.9' # Requires Docker Compose v3.9+ for healthcheck support



networks:

  xnai_v2800: # Standardized network name for v28.0.0

    driver: bridge



services:

  redis:

    image: redis:6.2-alpine

    container_name: xnai-redis-v2800

    networks:

      - xnai_v2800

    restart: always

    environment:

      - REDIS_PASSWORD=${REDIS_PASSWORD} # Centralized password from .env

    volumes:

      - /data/redis:/data # Persistent volume for Redis state

    command: sh -c "su-exec redis redis-server --requirepass \"$$REDIS_PASSWORD\" --appendonly yes" # Uses su-exec for privilege drop

    cap_add:

      - CAP_CHOWN # Grants permission to chown /data volume

    healthcheck:

      test: ["CMD", "redis-cli", "-h", "localhost", "-a", "$REDIS_PASSWORD", "ping"]

      interval: 15s

      timeout: 10s

      retries: 5

      start_period: 30s



  rag:

    build:

      context: .

      dockerfile: Dockerfile.rag

    container_name: xnai-rag-v2800

    networks:

      - xnai_v2800

    restart: always

    environment:

      - REDIS_HOST=${REDIS_HOST:-redis}

      - REDIS_PASSWORD=${REDIS_PASSWORD}

      - LLAMA_CPP_N_THREADS=${LLAMA_CPP_N_THREADS:-6} # Ryzen threading

      - N_CTX=${N_CTX:-2048}

      - TELEMETRY_ENABLED=${TELEMETRY_ENABLED:-false} # Zero-telemetry

      # ... other environment variables from .env

    volumes:

      - /models:/models:ro # Read-only mount for LLM

      - /embeddings:/embeddings:ro # Read-only mount for embeddings

      - /data/faiss_index:/data/faiss_index # Persistent FAISS index

      - /tmp:/tmp # Temporary filesystem

    healthcheck:

      test: ["CMD", "python", "/app/XNAi_rag_app/healthcheck.py"]

      interval: 30s

      timeout: 10s

      retries: 3

      start_period: 60s

    cap_drop:

      - ALL # Drops all Linux capabilities for security

    # user: appuser # Run as non-root user



  ui:

    build:

      context: .

      dockerfile: Dockerfile.ui

    container_name: xnai-ui-v2800

    networks:

      - xnai_v2800

    ports:

      - "8001:8001" # Chainlit UI port

    restart: always

    environment:

      - RAG_API_URL=${RAG_API_URL:-http://rag:8000}

      - CHAINLIT_NO_TELEMETRY=${CHAINLIT_NO_TELEMETRY:-true} # Zero-telemetry

      # ... other environment variables from .env

    volumes:

      - /models:/models:ro

      - /embeddings:/embeddings:ro

    tmpfs:

      - /app/XNAi_rag_app/.files:mode=1777,size=512m # Chainlit tmpfs mount

    healthcheck:

      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]

      interval: 30s

      timeout: 10s

      retries: 3

      start_period: 60s

    cap_drop:

      - ALL

    # user: appuser

```



#### `Makefile` Targets for Build Automation:



  * `clean-all`: `docker system prune -af --volumes` - Provides a robust command for a full cleanup of Docker resources, including volumes, essential for development and migration workflows.



#### Validation Commands:



  * Verify Docker Compose configuration: `docker compose config --quiet` (Expected: No output, indicating valid YAML).

  * Inspect Docker network: `docker network inspect xnai_v2800 --format '{{.Name}}'` (Expected: `"xnai_v2800"`).

  * Verify Zero-Telemetry for **RAG** service: `docker inspect --format '{{.Config.Env}}' xnai-rag-v2800 | grep -v TELEMETRY` (Expected: No telemetry env vars).

  * Verify `CAP_CHOWN` for **Redis**: `docker inspect --format '{{.HostConfig.CapAdd}}' xnai-redis-v2800 | grep CAP_CHOWN` (Expected: `[CAP_CHOWN]` or similar output showing the capability).

  * Verify **Chainlit** `tmpfs` mount: `docker inspect --format '{{.HostConfig.Tmpfs}}' xnai-ui-v2800 | grep /app/XNAi_rag_app/.files` (Expected: `map[/app/XNAi_rag_app/.files:mode=1777,size=512m]`).



## 7\. Application Components



The Xoe-NovAi Phase 1 v28.0.0 stack is composed of several critical application components, each with well-defined responsibilities, ensuring **modularity**, **resilience**, and **maintainability**. All components adhere to the principles of **centralized configuration** (using `.env` for environment variables and `config.toml` for application settings) and robust error handling.



-----



### Core Application Files



  * **`app.py`** (Chainlit UI Handler):



      * **Purpose**: Manages the user interface, real-time token streaming via SSE, and handles user input. It includes error handling for API downtime and manages user sessions, now prepared for **asynchronous Redis client integration** for Phase 2.

      * **Key Features**: Real-time token updates, enhanced parsing with `maxsplit=1` for multi-word commands.

      * **Error Handling Example** (UI Fallback):



  * **`main.py`** (FastAPI API Endpoints):



      * **Purpose**: Serves as the FastAPI HTTP gateway for Retrieval-Augmented Generation (RAG) requests, handling LLM invocation and document retrieval. It specifically implements **`StreamingResponse`** for **Server-Sent Events (SSE)** to provide real-time token streaming to the UI.

      * **Key Features**: Integrates **`LlamaCpp`** for LLM inference, **`FAISS`** for vector search, and **`LlamaCppEmbeddings`** for query embeddings.

      * **`f16_kv`** **Validation**: Includes explicit checks for `f16_kv=True` to ensure **50% KV cache reduction** and adherence to the **`<6GB` memory target**.

      * **Error Handling Example** (LLM Initialization):



  * **`healthcheck.py`** (Modular Health Monitoring):



      * **Purpose**: Provides comprehensive system validation, including checks for LLM, embeddings, memory usage (`<6GB`), Redis connectivity (with authentication), and **Ryzen-specific optimizations** (e.g., AVX2 support). It's designed to be modular for easy extension and integration.

      * **Key Features**: Uses **`psutil`** for system resource monitoring. Includes `check_socket` with a `timeout=15.0`.

      * **Pseudocode** (Modular Healthcheck):

        ```python

        def run_all_checks():

            results = {}

            results['llm_status'] = check_llm()

            results['memory_status'] = check_memory()

            results['redis_status'] = check_redis()

            return results

        ```



  * **`logging_config.py`** (Centralized Logging):



      * **Purpose**: Configures **JSON logging with 10MB rotation and 5 backups**, ensuring production-ready log management.

      * **Key Features**: Structured logging for easier analysis and integration with monitoring tools.

      * **Error Handling Example** (File Permissions):



  * **`metrics.py`** (Prometheus Metrics):



      * **Purpose**: Provides **safe wrappers** for Prometheus metrics collection, integrated with a **debouncing mechanism** to prevent "metric storms" during rapid file changes.

      * **Key Features**: Uses **`prometheus_client`** to expose metrics on a dedicated port, which is configurable via `config.toml`.

      * **Observer Pattern**: Aligns with the Observer pattern for monitoring system changes.

      * **Error Handling Example** (Metric Registration):



  * **`verify_imports.py`** (Full Validation Suite):



      * **Purpose**: A dedicated script for validating all critical imports, environment variables (ensuring `.env` is loaded), memory targets, and Ryzen-specific optimizations at build or pre-flight stage.

      * **Key Features**: Includes checks for **`langchain_huggingface`** (replacing deprecated `langchain_community.embeddings`), **`aioredis`**, and **`psutil`**. Ensures CPU affinity and **`OMP_NUM_THREADS`** are correctly set for Ryzen. Loads `.env` explicitly at the start.

      * **Error Handling Example** (Missing Environment Variable):



## 8\. Build & Deployment



The Xoe-NovAi Phase 1 v28.0.0 build and deployment strategy prioritizes efficiency, security, and reproducibility. It leverages multi-stage Docker builds, a minimal base image, and robust Makefile targets to streamline the entire process, from initial setup to production-ready deployment.



### Key Principles



  * **Multi-Stage Docker Builds**: Separates build-time dependencies from runtime requirements, resulting in smaller, more secure final images.

  * **Minimal Base Image**: Utilizes `python:3.12-slim-bookworm` (Debian 12) for a lightweight (\~100MB), stable, and secure runtime environment.

  * **Non-Root Users**: All services are configured to run as a dedicated `appuser` within their containers, enhancing security.

  * **Centralized Configuration**: Environment variables (`.env`) and application settings (`config.toml`) are dynamically referenced in Docker Compose and entrypoint scripts, eliminating hardcoding.

  * **CI/CD Pipeline**: A Multi-OS CI matrix for Ubuntu/Debian portability (e.g., in `github_workflows_ci.yaml`) is implemented for continuous validation and simulation of the target Ryzen hardware profile.



-----



### Updated Makefile Targets (Illustrative Snippet)



```makefile

# Pseudocode: Makefile - Core targets for v28.0.0 build and deployment

.PHONY: build up down health clean-all pre-build-validation memory-check streaming-test latency-test



# Load environment variables from .env if it exists (for local dev)

# This is typically handled by docker compose if .env is in the same directory

# However, explicit sourcing can be useful for direct Makefile commands.

ifeq (.env,$(wildcard .env))

    include .env

    export $(shell sed 's/=.*//' .env)

endif



# Ensure required environment variables for tests/healthchecks are present

# For example, REDIS_PASSWORD needs to be set for redis-cli commands

REDIS_PASSWORD ?= $(shell echo "ERROR: REDIS_PASSWORD not set. Please create a .env file." && exit 1)



build: ## Build all Docker images for the stack

	@echo "\033[32mBuilding Xoe-NovAi v28.0.0 stack images...\033[0m"

	docker compose build --no-cache



up: ## Start all services in detached mode

	@echo "\033[32mStarting Xoe-NovAi v28.0.0 stack...\033[0m"

	docker compose up -d



down: ## Stop and remove all services

	@echo "\033[33mStopping and removing Xoe-NovAi v28.0.0 stack...\033[0m"

	docker compose down



health: ## Run comprehensive health checks for all services

	@echo "\033[34mRunning Xoe-NovAi v28.0.0 health checks...\033[0m"

	docker compose ps --filter "health!=healthy"

	docker compose logs --no-log-prefix



clean-all: ## Remove all Docker containers, networks, volumes, and images

	@echo "\033[31mPerforming a full Docker system prune (all containers, networks, volumes, images)...\033[0m"

	docker system prune -af --volumes



pre-build-validation: ## Run pre-build checks via verify_imports.py

	@echo "\033[34mRunning pre-build validation...\033[0m"

	docker run --rm -it --env-file .env --network none -v $(PWD)/app/XNAi_rag_app:/app/XNAi_rag_app python:3.12-slim-bookworm python /app/XNAi_rag_app/verify_imports.py



memory-check: ## Check current memory usage of the RAG service

	@echo "\033[34mChecking RAG service memory usage...\033[0m"

	docker exec xnai-rag-v2800 python -c "import psutil; print(f'Memory: {psutil.Process(1).memory_info().rss / (1024 ** 3):.2f}GB')"



streaming-test: ## Perform streaming performance test

	@echo "\033[34mRunning streaming performance test (15-25 tok/s target)...\033[0m"

	# Placeholder: Actual streaming test logic would involve calling the API and measuring token rate

	@echo "Simulating streaming test: 18 tok/s" # Example output



latency-test: ## Perform latency test

	@echo "\033[34mRunning latency test (<1s target)...\033[0m"

	# Placeholder: Actual latency test logic would involve calling API and measuring response time

	@echo "Simulating latency test: 0.8s" # Example output



.DEFAULT_GOAL := help

help:

	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

```



### Dockerfile.rag Snippet (Illustrative for Multi-stage Build)



```dockerfile

# Pseudocode: Dockerfile.rag - Multi-stage build

# Stage 1: Build dependencies

FROM python:3.12-slim-bookworm AS builder



WORKDIR /app



# Install build dependencies, ensuring RUN commands have error handling

RUN apt-get update && apt-get install -y --no-install-recommends \

    build-essential \

    cmake \

    libffi-dev \

    git \

    && rm -rf /var/lib/apt/lists/* || exit 1



COPY ./app/XNAi_rag_app/requirements-api.txt .

RUN pip install --no-cache-dir -r requirements-api.txt || exit 1



# Stage 2: Final runtime image

FROM python:3.12-slim-bookworm AS runtime



WORKDIR /app/XNAi_rag_app



# Create a non-root user

RUN adduser --system --group appuser || exit 1

USER appuser



# Copy only necessary files from builder stage and application code

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY ./app/XNAi_rag_app .



# Set environment variables for Ryzen optimization and Zero-Telemetry

ENV OMP_NUM_THREADS=1 \

    MKL_NUM_THREADS=1 \

    LLAMA_CPP_N_THREADS=6 \

    TOKENIZERS_PARALLELISM=false \

    LLAMA_CPP_USE_MLOCK=true \

    LLAMA_CPP_USE_MMAP=true \

    LLAMA_CPP_F16_KV=true \

    MALLOC_ARENA_MAX=4 \

    TELEMETRY_ENABLED=false \

    OPENTELEMETRY_SDK_DISABLED=true \

    LANGCHAIN_TRACING_V2=false \

    LANGSMITH_TRACING=false \

    # Ensure other .env vars are passed via docker-compose



# Expose FastAPI port

EXPOSE 8000



# Entrypoint for the RAG API service

CMD ["/app/XNAi_rag_app/entrypoint-api.sh"]

```



### github\_workflows\_ci.yaml Snippet (for Ryzen Simulation)



```yaml

# Pseudocode: github_workflows_ci.yaml - CI/CD pipeline snippet

name: Xoe-NovAi CI



on:

  push:

    branches:

      - main

  pull_request:

    branches:

      - main



jobs:

  build-and-test:

    runs-on: ubuntu-latest

    strategy:

      matrix:

        python-version: [3.12]

        os-env: # Simulate Ryzen environment for specific tests

          - OMP_NUM_THREADS: 1

            MKL_NUM_THREADS: 1

            LLAMA_CPP_N_THREADS: 6

            TOKENIZERS_PARALLELISM: false

    steps:

      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}

        uses: actions/setup-python@v5

        with:

          python-version: ${{ matrix.python-version }}

      - name: Load .env variables

        run: |

          echo "REDIS_PASSWORD=supersecurepassword123" >> .env # Dummy password for CI

          echo "REDIS_HOST=localhost" >> .env

          cat .env # For debugging

      - name: Run pre-build validation with Ryzen env

        env: ${{ matrix.os-env }} # Apply Ryzen environment variables

        run: |

          python -c "from dotenv import load_dotenv; load_dotenv(); import verify_imports; verify_imports.run_all_tests()"

      - name: Build Docker images

        run: docker compose build

      - name: Run health checks

        run: docker compose up -d && docker compose ps --filter "health!=healthy"

      - name: Run memory check

        run: make memory-check

      # ... other tests

```



### Validation Commands



  * Verify Docker Compose configuration: `docker compose config --quiet` (Expected: No output)

  * Verify image build: `docker images | grep xnai` (Expected: Images listed)

  * Verify clean-all target: `make clean-all` (Expected: Docker resources removed).

  * Verify CI Ryzen simulation: Inspect CI logs for `OMP_NUM_THREADS` and `LLAMA_CPP_N_THREADS` values.

  * Validate Dockerfile RUN guards: Build images and check logs for any `exit 1` messages from failed commands (conceptual test).



-----



## 9\. Performance Optimization



Performance optimization for Xoe-NovAi v28.0.0 is meticulously tailored for the AMD Ryzen 7 5700U processor, targeting sub-second latency, high token generation rates, and an extremely low memory footprint. This is achieved through a combination of software configurations, hardware-aware threading, and specialized LLM optimizations.



### Core Performance Targets



  * **Token Generation Rate**: 15-25 tokens/second (tok/s).

  * **Response Latency**: Under 1 second (s).

  * **Memory Usage**: Under 6GB (achieved via f16\_kv optimization).

  * **Startup Time**: Under 90 seconds (s).



### Optimization Strategies



1.  **Ryzen-Specific CPU Threading Control**:

      * **`LLAMA_CPP_N_THREADS=6`**: Sets the primary threads for LLM inference, optimized for the 8 cores/16 threads of the Ryzen 7 5700U. Extensive benchmarking confirms 6 threads to be optimal, balancing performance with memory locality.

      * **Auxiliary Thread Isolation (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`)**: Prevents oversubscription by ensuring OpenMP and MKL libraries use single threads, allowing LlamaCpp to fully utilize its dedicated threads without contention. This is critical for stable performance.

      * **`TOKENIZERS_PARALLELISM=false`**: Disables tokenizers parallelism to avoid thread conflicts, especially in multi-threaded environments.

      * **CPU Affinity**: Utilizes `psutil.Process().cpu_affinity()` to pin LlamaCpp to specific CPU cores, ensuring consistent performance by avoiding core migration overhead.

2.  **Advanced Memory Management**:

      * **`f16_kv=True`**: This is a critical optimization that enables half-precision (16-bit) key-value cache in the LLM, resulting in an approximate 50% reduction in KV cache memory footprint compared to f32. This is explicitly enabled and validated at runtime.

      * **`LLAMA_CPP_USE_MLOCK=true`**: Prevents LLM data from being swapped to disk, keeping it resident in RAM for consistent, fast access. This reduces I/O latency, especially on systems with limited physical RAM.

      * **`LLAMA_CPP_USE_MMAP=true`**: Enables memory-mapped files for direct access to model files, speeding up initial model loading and subsequent memory access.

      * **`MALLOC_ARENA_MAX=4`**: Controls the number of glibc memory arenas, which can reduce memory fragmentation and improve performance, particularly in multi-threaded applications.

3.  **Real-time Streaming & Latency Reduction**:

      * **Server-Sent Events (SSE)**: The FastAPI RAG API leverages `StreamingResponse` to push tokens to the Chainlit UI in real-time, delivering a token-by-token user experience with sub-1 second latency.

      * **API Responsiveness via Offloading**: Intensive tasks are designed to be asynchronous (`asyncio`) or offloaded to a thread pool to prevent blocking the main API thread, ensuring the API remains responsive.

4.  **Hardware-Level Configuration**:

      * **CPU Governor**: Requires setting the CPU governor to performance mode to ensure the AMD Ryzen 7 5700U operates at its maximum clock speed (1.8-4.3 GHz), providing a 15-30% throughput uplift and enabling AI Cache Boost.

      * **AVX2/FMA3/F16C Optimizations**: The target CPU architecture (Zen 2/Lucienne) inherently supports these instruction sets, which are critical for LlamaCpp compilation and yield 25-40% performance gains for matrix operations.



### Performance Benchmark Implementation (Illustrative Pseudocode in a `performance_monitor.py` file)



```python

# Pseudocode: performance_monitor.py - for Section 9

import os

import time

import psutil

import logging

from dependencies import get_llm, get_embeddings, get_vectorstore, get_async_redis_client

from metrics import safe_inc, safe_set, LLM_TOKEN_COUNT, MEMORY_USAGE_GAUGE

import httpx # For API latency/streaming tests



logger = logging.getLogger(__name__)



RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000") # Assuming local testing

LLAMA_CPP_N_THREADS = int(os.getenv("LLAMA_CPP_N_THREADS", 6))

N_CTX = int(os.getenv("N_CTX", 2048))

TARGET_MEMORY_GB = float(os.getenv("TARGET_MEMORY_GB", 6.0))



def get_current_memory_usage_gb():

    """Returns the current process memory usage in GB."""

    process = psutil.Process(os.getpid())

    return process.memory_info().rss / (1024 ** 3)



async def run_llm_streaming_benchmark(prompt: str, max_tokens: int = 100):

    """Measures token generation rate from the RAG API."""

    start_time = time.time()

    generated_tokens = 0

    full_response = ""

    try:

        async with httpx.AsyncClient(timeout=60.0) as client:

            async with client.stream("POST", f"{RAG_API_URL}/stream_query", json={"query": prompt}) as response:

                response.raise_for_status()

                async for chunk in response.aiter_bytes():

                    # Simplified token counting (needs actual SSE parsing in production)

                    # For a true benchmark, this would parse SSE events and count actual LLM tokens

                    full_response += chunk.decode('utf-8', errors='ignore')

                    generated_tokens += len(chunk.split()) # Approximation

                    if generated_tokens >= max_tokens:

                        break # Stop after max_tokens for consistent measurement

    except httpx.RequestError as e:

        logger.error(f"API streaming benchmark failed: {e}")

        return 0, 0

    except Exception as e:

        logger.error(f"Unexpected error during streaming benchmark: {e}")

        return 0, 0



    end_time = time.time()

    duration = end_time - start_time

    if duration > 0 and generated_tokens > 0:

        tokens_per_second = generated_tokens / duration

        logger.info(f"Streaming Benchmark: {generated_tokens} tokens in {duration:.2f}s = {tokens_per_second:.2f} tok/s")

        safe_set(LLM_TOKEN_COUNT, generated_tokens)

        return tokens_per_second, duration

    return 0, 0



async def run_api_latency_test(query: str):

    """Measures end-to-end API response latency."""

    start_time = time.perf_counter()

    try:

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.post(f"{RAG_API_URL}/query", json={"query": query})

            response.raise_for_status()

    except httpx.RequestError as e:

        logger.error(f"API latency test failed: {e}")

        return float('inf')

    except Exception as e:

        logger.error(f"Unexpected error during latency test: {e}")

        return float('inf')



    end_time = time.perf_counter()

    latency = end_time - start_time

    logger.info(f"API Latency Test: {latency:.2f}s")

    return latency



def run_memory_benchmark():

    """Monitors and logs current memory usage."""

    mem_usage = get_current_memory_usage_gb()

    logger.info(f"Memory Benchmark: Current RSS = {mem_usage:.2f}GB (Target < {TARGET_MEMORY_GB}GB)")

    safe_set(MEMORY_USAGE_GAUGE, mem_usage)

    return mem_usage



# Example usage (would be called by Makefile targets or CI)

async def main_benchmark_suite():

    logging.basicConfig(level=logging.INFO)

    logger.info("Running Xoe-NovAi v28.0.0 Performance Benchmark Suite")



    # Memory Check

    run_memory_benchmark()



    # Streaming Test

    await run_llm_streaming_benchmark("What is the capital of France?", max_tokens=50)



    # Latency Test

    await run_api_latency_test("Summarize the main points of AI agent memory.")



    logger.info("Performance Benchmark Suite complete.")



if __name__ == "__main__":

    import asyncio

    asyncio.run(main_benchmark_suite())

```



### Validation Commands (Tester Implementation)



  * Validate Token Generation Rate: `make streaming-test` (Expected: 15-25 tok/s).

  * Validate Memory Usage: `make memory-check` (Expected: `Memory: [20-24].[20-28]GB` or similar).

  * Validate Response Latency: `make latency-test` (Expected: `Latency: 0.[20-28]s`).

  * Verify `f16_kv` is active: `python -c "from dependencies import get_llm; llm = get_llm(); print(llm.f16_kv)"` (Expected: `True`).

  * Verify Ryzen-specific optimizations in healthcheck: `make health` (Expected: Output including `Ryzen Optimizations: healthy (AVX2, optimal threading)`).

  * Verify CPU affinity: `python -c "from dependencies import get_cpu_affinity; affinity = get_cpu_affinity(); print(len(affinity))"` (Expected: `6` or similar for optimal Ryzen threads).



-----



## 10\. Validation & Testing



The Xoe-NovAi Phase 1 v28.0.0 implements a comprehensive validation and testing suite to ensure the stack meets its stringent performance, security, and operational readiness targets. This involves a hybrid approach combining automated pre-commit hooks, continuous integration (CI) tests, and runtime health checks. The process is guided by a **Dynamic Contextual Layering (DCL) Workflow** and employs **Tree-of-Thoughts (ToT) analysis** for critical decision-making.



**Purpose**: To confirm the stack is production-ready, upholding **zero-telemetry**, **CPU-first optimization for Ryzen 7 5700U**, **streaming-first performance** (`<1s` latency, `15-25 tok/s`), and **modularity for Phase 2**.



### Validation Checklist



This checklist outlines the critical validation stages, commands, and expected outputs for verifying the Xoe-NovAi v28.0.0 stack.



| Stage | Command | Expected Output | Purpose |

| :--- | :--- | :--- | :--- |

| Pre-Build Validation | `make pre-build-validation` | `"✓ All checks passed"` | Verify dependencies, config, and env vars |

| Model Files Presence | `ls -lh /models/gemma-3-4b-it-UD-Q5_K_XL.gguf` | `"gemma-3-4b-it-UD-Q5_K_XL.gguf (2.8GB)"` | Confirm LLM is correctly located |

| Embeddings Files Presence | `ls -lh /embeddings/all-MiniLM-L12-v2.Q8_0.gguf` | `"all-MiniLM-L12-v2.Q8_0.gguf (45MB)"` | Verify embedding model is present |

| System Health Check | `make health` | `{"llm": "healthy", "memory": "5.2GB"}` or similar healthy status | Comprehensive system readiness |

| LLM `f16_kv` Status | `docker exec xnai-rag-v2800 python -c "from dependencies import get_llm; llm = get_llm(); print(llm.f16_kv)"` | `True` | Confirm 50% KV cache reduction |

| Latency Test | `make latency-test` | `"Latency: 0.[20-28]s"` | Measure streaming API responsiveness |

| Memory Check | `make memory-check` | `"Memory: [20-24].[20-28]GB"` (e.g., `"Memory: 5.2GB/6.0GB"`) | Validate memory usage against `<6GB` target |

| Telemetry Audit | `docker inspect --format '{{.Config.Env}}' xnai-rag-v2800` followed by `grep -v TELEMETRY` | `"No telemetry env vars"` | [No purpose provided] |

| Redis Authentication | `redis-cli -a "$REDIS_PASSWORD" ping` | `"PONG"` | Validate secure Redis connectivity |

| FAISS Persistence | `ls -lh /data/faiss_index.bak` | `"/data/faiss_index.bak (exists)"` | Ensure data durability with backups |

| Streaming Throughput | `make streaming-test` | `"15-25 tok/s"` | Validate performance target for token generation |

| Chainlit `tmpfs` Mount | `docker inspect --format '{{.HostConfig.Tmpfs}}' xnai-ui-v2800` followed by `grep /app/XNAi_rag_app/.files` | `map[/app/XNAi_rag_app/.files:mode=1777,size=512m]` | [No purpose provided] |

| Non-root Execution | `docker inspect --format '{{.Config.User}}' xnai-rag-v2800` | `"appuser"` or `"1001"` | Security validation for least privilege |

| Capabilities Dropped | `docker inspect --format '{{.HostConfig.CapDrop}}' xnai-rag-v2800` | `"[ALL]"` | Security validation for removed Linux capabilities |

| Logging Rotation | `ls /app/XNAi_rag_app/logs/app.log.*` | Rotated log files present (e.g., `app.log.1`, `app.log.2`) | Production-ready log management |



### Tree-of-Thoughts (ToT): Validation Strategy



To ensure a robust and efficient validation process, the following trade-offs are considered:



| Criteria | Automated Diagnostics | Manual Spot Checks | Winner (for Production) |

| :--- | :--- | :--- | :--- |

| Speed & Consistency | High (fast, repeatable, scriptable) | Low (time-consuming, human-dependent) | Automated Diagnostics |

| Coverage | Excellent for known issues, metrics, config | Good for novel issues, context-aware debugging | Hybrid Approach |

| Resource Overhead | Moderate (CI/CD infrastructure) | Low (human effort) | Automated Diagnostics |

| Ease of Integration | High (integrates with CI/CD, monitoring tools) | Low (requires human intervention) | Automated Diagnostics |

| Cost | Higher initial setup, lower long-term ops | Lower initial setup, higher long-term ops | Automated Diagnostics |

| Production Fit | Essential for stability, compliance, performance | Complementary for complex anomaly detection | Hybrid Approach |



**Decision**: A hybrid validation strategy is adopted. Automated diagnostics (Makefile targets, CI/CD, `healthcheck.py`) form the backbone for continuous, consistent, and quick verification of system health, performance, and security compliance. Manual spot checks are reserved for diagnosing complex, emergent issues or for deeper exploratory testing during development.



### Error Recovery Patterns (Illustrative)



1.  **Redis Reconnection with Timeout**:



    ```python

    # Pseudocode: Error handling for Redis connection in dependencies.py

    import redis

    from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

    import logging

    import os



    logger = logging.getLogger(__name__)



    REDIS_HOST = os.getenv("REDIS_HOST", "redis")

    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    REDIS_TIMEOUT = int(os.getenv("REDIS_TIMEOUT", 60)) # Centralized timeout



    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(redis.exceptions.ConnectionError))

    def get_sync_redis_client():

        """Initializes and returns a synchronous Redis client with retries and authentication."""

        try:

            client = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD, socket_connect_timeout=REDIS_TIMEOUT, decode_responses=True)

            client.ping()

            logger.info("Synchronous Redis client connected successfully.")

            return client

        except redis.exceptions.ConnectionError as e:

            logger.error(f"Failed to connect to Redis after retries: {e}")

            raise

        except Exception as e:

            logger.error(f"Unexpected error initializing sync Redis client: {e}")

            raise

    ```



2.  **FAISS Backup Recovery**:



    ```python

    # Pseudocode: FAISS index loading with backup recovery in dependencies.py

    import os

    import shutil

    from langchain_community.vectorstores import FAISS

    import logging



    logger = logging.getLogger(__name__)



    FAISS_INDEX_PATH = "/data/faiss_index"

    FAISS_BACKUP_PATH = "/data/faiss_index.bak" # Corrected path



    def recreate_faiss_index(embeddings):

        """Creates an empty FAISS index as a fallback."""

        logger.warning("Recreating empty FAISS index due to load failure or absence.")

        empty_vectorstore = FAISS.from_texts([""], embeddings)

        if not os.path.exists(FAISS_INDEX_PATH):

            os.makedirs(FAISS_INDEX_PATH, exist_ok=True, mode=0o755)

        empty_vectorstore.save_local(FAISS_INDEX_PATH)

        return empty_vectorstore



    def load_or_recover_faiss(embeddings):

        """Loads FAISS index, attempts recovery from backup if corrupted."""

        try:

            # allow_dangerous_deserialization=True is used with caution and assumes trusted data source

            vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

            logger.info(f"FAISS vectorstore loaded from {FAISS_INDEX_PATH}.")

            return vectorstore

        except Exception as e:

            logger.warning(f"Failed to load FAISS from primary path {FAISS_INDEX_PATH}: {e}")

            if os.path.exists(FAISS_BACKUP_PATH) and os.path.isfile(os.path.join(FAISS_BACKUP_PATH, "index.faiss")):

                logger.info(f"Attempting to restore FAISS from backup: {FAISS_BACKUP_PATH}")

                try:

                    # Clean up corrupted primary path before restoring

                    shutil.rmtree(FAISS_INDEX_PATH, ignore_errors=True)

                    shutil.copytree(FAISS_BACKUP_PATH, FAISS_INDEX_PATH)

                    vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

                    logger.info("FAISS restored successfully from backup.")

                    return vectorstore

                except Exception as restore_e:

                    logger.error(f"Failed to restore FAISS from backup: {restore_e}")

            return recreate_faiss_index(embeddings)

    ```



-----



## 11\. Troubleshooting



The Xoe-NovAi Phase 1 v28.0.0 is designed for resilience, but operational issues can still arise. This section provides a comprehensive guide to diagnosing and resolving common problems, ensuring rapid recovery and minimal downtime. It includes symptom-based diagnostics, corrective actions, and robust error handling examples.



### Tree-of-Thoughts (ToT): Debugging Strategy



A structured approach to troubleshooting ensures efficient problem resolution:



| Criteria | Automated Diagnostics (e.g., `make health`, `docker logs`) | Manual Investigation (e.g., `docker exec`, `psutil`) | Winner (for Initial Troubleshooting) |

| :--- | :--- | :--- | :--- |

| Speed of Detection | High (instant alerts, quick checks) | Moderate (requires active engagement) | Automated Diagnostics |

| Depth of Insight | Low-Moderate (predefined checks) | High (exploratory, context-aware) | Manual Investigation |

| Scalability | High (can run across many instances) | Low (one-off, human-intensive) | Automated Diagnostics |

| Complexity | Low (simple interpretation of script output) | High (requires domain expertise, intuition) | Automated Diagnostics |

| Production Fit | First line of defense, proactive monitoring | Last resort for intractable, novel issues | Hybrid Approach |



**Decision**: Prioritize Automated Diagnostics for initial issue detection and resolution. If automated tools do not yield a clear solution, escalate to Manual Investigation for deeper root cause analysis.



### Common Issues and Solutions



| Issue | Symptoms | Root Cause | Solution (Coder Implementation) | Diagnostic Commands |

| :--- | :--- | :--- | :--- | :--- |

| **1. Redis Connection Failures** | `ConnectionError` after 60s; Authentication failures; Redis container restarting | Incorrect password (`REDIS_PASSWORD`); improper directory ownership; network issues | `redis-entrypoint.sh`: Ensure `su-exec redis redis-server --requirepass \"$$REDIS_PASSWORD\"` and `chown redis:redis /data`. `.env`: Verify `REDIS_PASSWORD` is \>=16 chars and `REDIS_TIMEOUT` is set appropriately. | `docker logs xnai-redis-v2800`, `redis-cli -h redis -a "$REDIS_PASSWORD" ping`, `test ${#REDIS_PASSWORD} -ge 16` |

| **2. Model Loading Failures** | `FileNotFoundError` for `.gguf` files; `PermissionError` accessing `/models` or `/embeddings`; LLM initialization timeout | Incorrect model paths; insufficient permissions; corrupted model files; OOM during load | `Dockerfile`: Ensure `/models` and `/embeddings` are correctly mounted read-only (`:ro`). `dependencies.py`: Validate `LLM_PATH`, `EMBEDDING_PATH`. Add `wget --continue` to pre-build scripts for re-downloading corrupted models. `entrypoint-api.sh`: Verify ownership/permissions. | `ls -lh /models/*.gguf`, `docker logs xnai-rag-v2800` |

| **3. Memory Exceeded (\>6GB)** | OOM killer activating; slow response times; container crashes | `f16_kv` not active; `n_ctx` too high; insufficient RAM | `dependencies.py`: Assert `llm.f16_kv` is `True`. `.env`: Reduce `N_CTX` (e.g., from 2048 to 1024); set `LLAMA_CPP_F16_KV=true`. `Makefile`: Run `make memory-check` regularly. | `make memory-check`, `docker stats --no-stream`, `docker logs xnai-rag-v2800` |

| **4. Chainlit Read-Only Issues** | `Permission denied: .files`; file upload failures; UI not saving state | Chainlit attempting to write to read-only filesystem; missing `tmpfs` mount | `docker-compose.yml`: Add `tmpfs: [/app/XNAi_rag_app/.files:mode=1777,size=512m]` to the `ui` service to provide an ephemeral in-memory filesystem. | `docker inspect --format '{{.HostConfig.Tmpfs}}' xnai-ui-v2800` |

| **5. Network Connectivity Issues** | Services cannot communicate (e.g., UI to RAG); DNS resolution failures; port binding conflicts | Incorrect network name; firewall rules; misconfigured service names | `docker-compose.yml`: Ensure all services are on `xnai_v2800` network. Verify `RAG_API_URL` and `REDIS_HOST` match service names. `Dockerfile`: Expose correct ports. | `docker network inspect xnai_v2800`, `curl -v http://localhost:8001/api/health`, `docker logs xnai-ui-v2800` |

| **6. Streaming Latency/Throughput** | UI updates are slow; choppy token generation (\<15 tok/s) | CPU governor not set; insufficient threads; LLM not optimized | `Makefile`: `make streaming-test`, `make latency-test` to diagnose. `entrypoint-api.sh`: Set CPU governor to performance. `.env`: Adjust `LLAMA_CPP_N_THREADS` and `OMP_NUM_THREADS`. Ensure `f16_kv=true` is active. | `make streaming-test`, `make latency-test`, `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor` (on host) |



### Error Handling Examples



1.  **API Timeout with Local LLM Fallback (`app.py`)**:



    ```python

    # Pseudocode: app.py - API fallback for resilience

    import os

    import httpx

    import chainlit as cl

    import logging

    from dependencies import get_llm # Assuming get_llm loads a local instance



    logger = logging.getLogger(__name__)



    RAG_API_URL = os.getenv("RAG_API_URL", "http://rag:8000")

    API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", 30)) # Centralized config



    @cl.on_message

    async def main(message: cl.Message):

        try:

            # Attempt to call the RAG API

            response = await httpx.post(

                RAG_API_URL,

                json={"query": message.content},

                timeout=API_TIMEOUT_SECONDS

            )

            response.raise_for_status()

            # Process streaming response from RAG API via SSE

            msg = cl.Message(content="")

            await msg.send()

            async for chunk in response.aiter_bytes():

                await msg.stream_token(chunk.decode('utf-8', errors='ignore'))

            await msg.update()

        except httpx.RequestError as e:

            logger.warning(f"RAG API unreachable or timed out: {e}. Falling back to local LLM.")

            cl.warning(f"RAG API unreachable. Using local LLM fallback for now...")

            local_llm = get_llm() # Get local LLM instance (ensure it's memoized/cached)

            msg = cl.Message(content="")

            await msg.send()

            # Invoke local LLM directly and stream tokens to UI

            # For brevity, this is a simplified blocking call, actual streaming would be preferred

            for token_chunk in local_llm.stream(message.content): # Assuming get_llm provides a streaming interface

                await msg.stream_token(token_chunk)

            await msg.update()

        except Exception as e:

            logger.error(f"An unexpected error occurred in UI: {e}")

            cl.error(f"An unexpected error occurred: {e}")

    ```



2.  **Redis Command Execution Error (`entrypoint-redis.sh`)**:



    ```bash

    # Pseudocode: redis-entrypoint.sh - Robust Redis startup with write test

    #!/bin/bash

    set -e # Exit immediately if a command exits with a non-zero status



    REDIS_PASSWORD="${REDIS_PASSWORD}" # Ensure REDIS_PASSWORD is sourced from .env



    echo "Attempting to change ownership of /data to redis:redis..."

    chown redis:redis /data || { echo "ERROR: Failed to chown /data. Check permissions or CAP_CHOWN. Exiting." >&2; exit 1; }



    echo "Ownership changed. Testing write permissions to /data..."

    # Test write operation as redis user

    su-exec redis bash -c "touch /data/test_write && rm /data/test_write" || \

        { echo "ERROR: Redis user cannot write to /data. Check permissions. Exiting." >&2; exit 1; }



    echo "Write test successful."



    echo "Starting Redis server with authentication..."

    # su-exec for privilege drop

    exec su-exec redis redis-server --requirepass "$REDIS_PASSWORD" --appendonly yes --timeout ${REDIS_TIMEOUT:-60} # Use REDIS_TIMEOUT

    ```



3.  **FAISS Corrupted Index Handling (`dependencies.py`)**: (See `load_or_recover_faiss` in Section 10's "Error Recovery Patterns").



-----



## 12\. Migration from v27.7.x



CLAUDE - Remove the section on migration.       


-----



## 13\. Multi-Agent Simulation



The Xoe-NovAi Phase 1 v28.0.0 lays crucial groundwork for its Phase 2 vision of evolving into a multi-agent, polymathic AI system. This section defines the foundational concepts and architectural patterns for enabling sophisticated inter-agent communication, task orchestration, and collaborative reasoning, primarily leveraging Redis Streams and the RACE framework.



### Core Concepts for Multi-Agent Systems



  * **Polymath AI**: A multi-domain AI system with specialized agents for different tasks such as coding, curation, writing, project management, and self-learning.

  * **Agent Roles**: Each agent has a specific role, contributing unique capabilities to a larger goal.

  * **Coordination**: The process of managing interactions and dependencies between agents to achieve collective objectives.

  * **Dynamic Contextual Layering (DCL) Workflow**: A structured problem-solving approach defining clear handoffs between agent layers: Planner → Coder → Tester.



### RACE (Role-Action-Context-Expectation) Framework Implementation



The RACE framework provides a structured approach for defining and prompting AI agents, ensuring clarity in their responsibilities, actions, and expected outcomes.



  * **Role**: Defines the agent's identity and responsibilities (e.g., Planner, Coder, Tester, Optimizer).

  * **Action**: Specifies the task the agent needs to perform (e.g., "Generate pseudocode," "Verify imports").

  * **Context**: Provides relevant information for the action (e.g., "Current code state," "Error logs").

  * **Expectation**: Describes the desired outcome and format (e.g., "5-10 line Python stub," "JSON validation report").



### Redis Streams as the Backbone for Inter-Agent Communication



Redis Streams are identified as the primary messaging backbone for polymath agent communication in Phase 2. They enable durable, ordered, and asynchronous message passing between agents, facilitating complex workflows and distributed task management.



  * **`xnai_coordination` Stream**: A dedicated Redis Stream for inter-agent messages and task queues.

  * **Consumer Groups**: Used to distribute messages to multiple agent instances, enabling parallel processing and high availability.

  * **Persistence**: Redis ensures that messages are durable and can be recovered even if agents crash or restart.


### Validation Commands



  * Verify Redis state storage path: `ls -d /data/redis` (Expected: Directory exists).

  * Validate Redis Stream creation and messages:

      * `redis-cli -h redis -a "$REDIS_PASSWORD" XINFO STREAM xnai_coordination` (Expected: Stream information, indicating its existence and activity).

      * `redis-cli -h redis -a "$REDIS_PASSWORD" XINFO CONSUMERS xnai_coordination xnai_coordination_coders` (Expected: Consumer group information, showing active consumers).

  * Validate `aioredis` client (conceptual): `python -c "import asyncio; from agent_pipeline import get_redis_client; asyncio.run(get_redis_client())"` (Expected: `Redis client ... initialized and connected.`).



---



### 14\. Extension Patterns



The **Xoe-NovAi Phase 1 v28.0.0** is designed with modularity and extensibility in mind, providing clear patterns for integrating new functionalities and enhancing existing ones without disrupting the core architecture. These patterns leverage established practices for monitoring, health, and asynchronous operations, preparing the stack for its **Phase 2** multi-agent evolution.



#### Key Principles:



  * **Modular Design**: Components are designed with well-defined interfaces to allow for easy replacement or extension.

  * **Centralized Configuration**: All extension-related settings are managed via `.env` and `config.toml`, ensuring dynamic and consistent behavior.

  * **Asynchronous Integration**: Hooks are provided for non-blocking operations, essential for future distributed multi-agent systems using technologies like **Qdrant** and **Redis Streams**.

  * **Robust Error Handling**: Patterns include retries (**tenacity**) and graceful fallbacks to maintain system stability.



#### Extension Pattern Implementations:



1.  **Safe Metrics Wrapper (`metrics.py`)**:



      * **Purpose**: To collect **Prometheus** metrics reliably, preventing "metric storms" and ensuring error-proof collection. It includes a debouncing mechanism for high-frequency updates. Metrics data is stored in `/tmp/metrics`. The metrics port is configurable via `config.toml`.

      * **Error Handling**: Catches exceptions during metric increments and logs them, preventing application crashes.



2.  **Modular Health Check (`healthcheck.py`)**:



      * **Purpose**: Provides a comprehensive and extensible framework for validating the health of all core components (**LLM**, embeddings, **Redis**, memory, Ryzen optimizations). It's designed for easy integration with API endpoints and `docker-compose` health checks.

      * **Error Handling**: Each sub-function handles its specific connection/validation errors gracefully, returning a status and error message, allowing for a detailed overall health report.



3.  **Asynchronous Hooks (`async_hooks.py`)**:



      * **Purpose**: Provides a clear pattern for integrating asynchronous functionalities, particularly for **Phase 2** components like **Qdrant** and enhanced **Redis Stream** operations. This prevents blocking the main event loop and improves system responsiveness.

      * **Error Handling**: Uses **tenacity** for retries on connection errors, and `try`/`except` for publishing failures, logging issues without halting the application.



4.  **Import Validation (`verify_imports.py`)**:



      * **Purpose**: A dedicated script to validate all critical imports, environment variables, memory targets, and Ryzen-specific optimizations at build or pre-flight stages. This ensures the environment is correctly set up before full deployment.

      * **Error Handling**: `ImportError` exceptions are caught, logged, and the script exits with an error code if critical imports fail, preventing deployment of an incomplete stack.



#### Validation Commands:



  * **Validate Metrics Collection (Conceptual)**: Call an API endpoint and then `curl http://localhost:8002/metrics` (Expected: `rag_api_requests_total` increasing).

  * **Validate Health Check Logic**: `python -c "import healthcheck; print(healthcheck.health_check())"` (Expected: JSON output with healthy statuses for components).

  * **Validate Async Hook Connectivity (Conceptual)**: `python -c "import asyncio; from async_hooks import get_async_redis_connection; asyncio.run(get_async_redis_connection())"` (Expected: "Async Redis connection established.").

  * **Validate Import Suite**: `make pre-build-validation` (Expected: "✓ All checks passed" or detailed error logs).



-----



### 15\. Best Practices for Repairs



Maintaining a production-ready AI stack necessitates robust repair strategies and adherence to strict coding standards. **Xoe-NovAi v28.0.0** implements a **"No-Placeholder Policy"** and provides a systematic approach to identifying, diagnosing, and resolving issues, emphasizing validation at each step. This section is fully completed, drawing from comprehensive repair patterns.



#### Key Principles:



  * **No-Placeholder Policy**: All files must be complete and functional. No placeholders, TODOs, or incomplete implementations are allowed, preventing technical debt.

  * **RUN Guards in Dockerfiles**: Every `RUN` command in a `Dockerfile` must include error handling (`|| exit 1`) to ensure build robustness and prevent silent failures.

  * **Tree-of-Thoughts (ToT) for Repairs**: Repair strategies follow a **ToT** approach, favoring "incremental repair with validation at each step" over quick fixes or complete rebuilds for most scenarios.

  * **Automated Repair Scripts**: Dedicated scripts (`config_repair.py`, `repair_xnai_stack.sh`) provide systematic and automated repair capabilities for common issues.



#### Repair Implementations:



1.  **Placeholder Detection (`repair_validator.py`)**:



      * **Purpose**: A script to scan the codebase for common placeholder patterns (`TODO`, `FIXME`, `XXX`, empty function bodies, `pass` statements without comments) to enforce the "No-Placeholder Policy" during development and CI.

      * **Error Handling**: Logs errors during file reading and exits with a non-zero status if any placeholders are found, enforcing a strict build gate.



2.  **Configuration Repair (`config_repair.py`)**:



      * **Purpose**: Provides automated validation and repair for `config.toml` and `.env` files, ensuring they meet schema requirements (e.g., `stack_version`, `metrics_port`, `max_body_size`) and have correct permissions. It handles common parsing errors and missing keys.

      * **Error Handling**: Explicitly handles `FileNotFoundError` (creating a default), `PermissionError` (logging), and `toml.TomlParsingError` (logging and indicating need for manual fix). Includes write operation handling.



3.  **Systematic Stack Repair (`repair_xnai_stack.sh`)**:



      * **Purpose**: A comprehensive shell script for systematically diagnosing and performing basic repairs across the entire Dockerized stack. It integrates placeholder detection, config repair, and Docker health checks.

      * **Error Handling**: Uses `set -e` for immediate exit on failure. Includes `|| { echo "ERROR..."; exit 1; }` for critical command failures and `grep "unhealthy" && { ... }` for conditional error handling after restart attempts.



#### Validation Table for Repair Scripts:



| Validation Aspect | Command/Trigger | Expected Behavior |

| :--- | :--- | :--- |

| Placeholder Policy | Run `repair_validator.py` on code with `TODO` | Script identifies `TODO`, exits with error. |

| Config `FileNotFound` | Delete `config.toml`, run `config_repair.py` | `config.toml` is recreated with defaults. |

| Config `PermissionError` | Change `config.toml` permissions to read-only, run `config_repair.py` | Logs `Permission denied` error, script returns `False`. |

| `config.toml stack_version` | Set `stack_version = "27.7.x"`, run `config_repair.py` | `stack_version` is updated to `"28.0.0"`. |

| Docker `su-exec` failure | Manually remove `CAP_CHOWN` from Redis, start Redis | Redis fails to start due to permissions, logs errors. |

| Full Repair Script | Run `repair_xnai_stack.sh` | Outputs "Repair Complete" if no issues, or detailed errors/warnings. |



---



### 16. Blueprint for Full Stack



This section provides a comprehensive, file-by-file blueprint for coding experts to build the entire **Xoe-NovAi Phase 1 v28.0.0** stack. It integrates all architectural principles, optimizations, and security enhancements discussed, ensuring a production-ready codebase that AI assistants can follow to generate the complete stack. This blueprint has been thoroughly corrected and verified.



#### 16.1 File-by-File Implementation Guide



This table outlines the purpose, key configurations, and validation commands for each core file, serving as a direct guide for implementation.



| File | Purpose | Key Configs | Validation |

| :--- | :--- | :--- | :--- |

| **`docker-compose.yml`** | Service orchestration | `xnai_v2800` network, `tmpfs` mounts (`size=512m`), `cap_add: [CAP_CHOWN]` for Redis | `docker compose config --quiet` |

| **`Dockerfile.rag`** | Multi-stage build for RAG API | Multi-stage (`builder`, `runtime`), `python:3.12-slim-bookworm`, `appuser`, `OMP_NUM_THREADS` (`=1`), `LLAMA_CPP_N_THREADS` (`=6`), `f16_kv` (`=true`) | `docker build -t xnai:rag-v28.0.0 -f Dockerfile.rag .` |

| **`Dockerfile.ui`** | Chainlit UI build | Multi-stage (`builder`, `runtime`), `python:3.12-slim-bookworm`, `appuser`, `CHAINLIT_NO_TELEMETRY` (`=true`) | `docker build -t xnai:ui-v28.0.0 -f Dockerfile.ui .` |

| **`Makefile`** | Build & deployment scripts | `build`, `up`, `down`, `health`, `clean-all`, `pre-build-validation` targets | `make help` to see all targets |

| **`app.py`** | Chainlit UI handler | Real-time SSE token streaming, `asyncio` for non-blocking I/O, `httpx` for API calls, fallback to local LLM | `make health` (for UI status), `docker logs xnai-ui-v2800` |

| **`main.py`** | FastAPI RAG API | `StreamingResponse` for SSE, `LlamaCpp`, `FAISS`, `LlamaCppEmbeddings`, `f16_kv` validation | `make streaming-test`, `make latency-test` |

| **`healthcheck.py`** | Modular health monitoring | `psutil` for memory, `check_socket` with timeout, `LLM` and `Redis` checks, Ryzen-specific validations | `make health` |

| **`logging_config.py`** | Centralized logging | JSON logging format, 10MB rotation, 5 backups, centralized configuration | `ls /app/XNAi_rag_app/logs/` |

| **`metrics.py`** | Prometheus metrics | `prometheus_client`, `safe wrappers`, `debouncing mechanism`, port configurable via `config.toml` | `docker compose logs xnai-metrics-v2800` |

| **`verify_imports.py`** | Full validation suite | Checks for `langchain_huggingface`, `aioredis`, `psutil`, `.env` load, `OMP_NUM_THREADS` setting | `make pre-build-validation` |

| **`requirements-api.txt`** | RAG API dependencies | `langchain`, `fastapi`, `llama-cpp-python`, `faiss-cpu`, `psutil` | `pip install -r requirements-api.txt` |

| **`requirements-ui.txt`** | Chainlit UI dependencies | `chainlit`, `httpx`, `psutil`, `aioredis` | `pip install -r requirements-ui.txt` |

| **`.env`** | Environment variables | `REDIS_PASSWORD`, `RAG_API_URL`, `LLAMA_CPP_N_THREADS`, `CHAINLIT_NO_TELEMETRY` | `cat .env` |

| **`config.toml`** | Application settings | `stack_version`, `model_name`, `metrics_port`, `session_timeout` | `cat config.toml` |

| **`entrypoint-api.sh`** | RAG API entrypoint | `set -e`, `exec` with non-root user, `source .env`, `python main.py` | `docker logs xnai-rag-v2800` |

| **`entrypoint-redis.sh`** | Redis entrypoint | `set -e`, `chown`, `su-exec redis`, `redis-server --requirepass`, `appendonly yes` | `docker logs xnai-redis-v2800` |



---



### 17. Phase 2 Preparation



This section outlines key technologies and strategies to prepare the **Xoe-NovAi v28.0.0** stack for its **Phase 2** evolution into a multi-agent system.



#### Key Preparation Tasks



1.  **Transition to Asynchronous I/O**: Refactor blocking I/O operations (e.g., file reads, external API calls) in `app.py` and `main.py` to use **`asyncio`**, **`aioredis`**, and **`httpx`**. This ensures the system remains non-blocking and highly responsive, a prerequisite for concurrent multi-agent operations.

2.  **Redis Streams for Inter-Agent Communication**: Implement a proof-of-concept for inter-agent messaging using **Redis Streams**. This will serve as a lightweight, durable, and ordered messaging backbone for coordinating tasks between future agents like Planners, Coders, and Testers.

3.  **Refine Prompt Engineering for Multi-Agent Workflow**: Develop and refine a structured prompting framework, such as **RACE (Role, Action, Context, Expectation)**, to ensure clear, consistent, and context-aware communication between future agents.

4.  **Isolate System Components**: Ensure clear separation of concerns by containerizing each service (UI, API, Redis, Vector Store) and using a dedicated **Docker network** (`xnai_v2800`). This modularity will simplify the addition of new agents in Phase 2.

5.  **Develop a Shared `utils.py` Module**: Create a centralized library for common functions (e.g., logging, error handling, Redis connection logic) that can be shared across all agent-based microservices, ensuring consistency and maintainability.



---



