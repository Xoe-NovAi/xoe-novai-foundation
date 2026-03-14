# Open‑Source Alternatives to Custom Components

**Date:** 2026-02-25
**Purpose:** Identify areas where the XNAi Foundation stack currently uses bespoke implementations but may benefit from leveraging mature open‑source projects instead of building/maintaining them in‑house.

## 1. Agent Bus / Message Streaming

- **Current:** Custom Redis Streams based `Agent Bus` with consumer groups and homegrown coordination logic.
- **Alternatives:**
  - [NATS](https://nats.io/) – lightweight, Go‑based, supports request/reply, streaming, and JetStream for persistence.
  - [Apache Kafka](https://kafka.apache.org/) – industry‑standard for heavy throughput, better for long-term retention than Redis.
  - [RabbitMQ](https://www.rabbitmq.com/) – feature‑rich AMQP broker with plugins.
  - [Apache Pulsar](https://pulsar.apache.org/) – built‑in multi‑tenant streaming.

*Recommendation:* Consider migrating to NATS/JetStream for simplicity or Kafka for scalability; the custom logic can be replaced by rich client libraries and built‑in monitoring.

## 2. Memory Bank & Vector Search

- **Current:** Custom SQLite/pgvector system with FTS5 integration and ad‑hoc embedding storage.
- **Alternatives:**
  - [Chroma](https://www.trychroma.com/) – Python vector DB, easy to install, local files or in‑memory.
  - [Milvus](https://milvus.io/) – enterprise‑grade, multi‑node vector database with indexing.
  - [Weaviate](https://weaviate.io/) – semantic graph vector store with plugin modules.

*Recommendation:* If local SQLite suffices, plugin style use Chroma; larger projects should evaluate Milvus/Weaviate to offload indexing and scaling concerns.

## 3. Configuration/Service Discovery

- **Current:** Consul for discovery, plus custom config loader.
- **Alternatives:**
  - [etcd](https://etcd.io/) – simple key‑value store used by Kubernetes.
  - [HashiCorp Vault](https://www.vaultproject.io/) – for secure secrets & config (though heavier).

*Recommendation:* Continue using Consul unless you need tighter Kubernetes integration, in which case etcd may be more portable.

## 4. Voice & Audio Utilities

- **Current:** In‑house voice module wrapping Whisper, Piper, wake‑word, AudioGuardian, etc.
- **Alternatives:**
  - [Mozilla DeepSpeech / Coqui](https://github.com/coqui-ai) – open STT engines.
  - [OpenAI Whisper OSS](https://github.com/openai/whisper) – used already but could be consumed via external service.  
  - [Rhasspy](https://rhasspy.readthedocs.io/) – offline voice assistant framework with modular components.
  - [Porcupine](https://picovoice.ai/) – wake word engine (open source option).

*Recommendation:* Evaluate Rhasspy as a drop‑in for the voice pipeline; it already handles wake words, STT, TTS and has a plugin architecture. That could replace much custom audio glue while maintaining offline and Torch‑free constraints.

## 5. Health/Monitoring & Metrics

- **Current:** Custom Prometheus metrics definitions and dashboards.
- **Alternatives:**
  - Rely on [Prometheus exporters](https://prometheus.io/docs/instrumenting/exporters/) for PostgreSQL, Redis, etc., instead of hand‑rolled metrics.
  - Use existing alerting rules in [Prometheus Alertmanager](https://prometheus.io/docs/alerting/alertmanager/) rather than custom health tables.

*Recommendation:* Continue with Prometheus but drop bespoke metric names; lean on standard exporters and community dashboards.

## 6. CLI & Agent Integration

- **Current:** Custom CLI abstraction (`cline`, `kat` dispatch functions).
- **Alternatives:**
  - Use [Click](https://click.palletsprojects.com/) or [Typer](https://typer.tiangolo.com/) for CLI creation.
  - Leverage [PyInvoke](http://www.pyinvoke.org/) or [Plumbum](https://plumbum.readthedocs.io/) for shell‑like task execution.

*Recommendation:* Standard CLI libraries provide argument parsing, help, and auto‑completion; they reduce maintenance burden.

## 7. Database Migrations

- **Current:** Alembic with custom env modifications.
- **Alternatives:** Alembic is already OSS; nothing to replace here, but keep migrations generic.

## 8. Curation Bridge & Crawl Worker

- **Current:** Custom curation/worker code using Langchain, SQLite, and custom bridging.
- **Alternatives:**
  - [Airbyte](https://airbyte.com/) or [Singer](https://www.singer.io/) for ETL tasks, though may be overkill.
  - [Scrapy](https://scrapy.org/) for crawling instead of bespoke `crawl.py` worker.

*Recommendation:* Evaluate Scrapy for larger or more complex crawl jobs; current custom code is acceptable for simple cases.

## 9. Other Custom Utilities

- AudioGuardian, Bluetooth router, wake‑word detector – see section above.
- Custom logging/telemetry wrappers – consider using [structlog](https://www.structlog.org/) or [loguru](https://github.com/Delgan/loguru).

---

### Next Steps
1. Add a strategy note summarizing this file in memory bank (already created).  
2. For each candidate, schedule a research job (e.g., `GAP‑XYZ: Evaluate NATS vs Redis Streams`).  
3. When Opus or other agents are engaged, have them generate migration plans or proof‑of‑concepts using the chosen OSS alternatives.

> **Goal:** reduce maintenance overhead and leverage community‑tested components without sacrificing sovereignty or offline capabilities.

**End of alternative review.**