---
title: Readme
service: Jaeger
source_urls: ["/tmp/tmp_98k71au/repo/docs/adr/README.md"]
scraped_at: 2026-02-17T00:27:55.978273
content_hash: 0fc850bd99b2ff782db80924fc2248c159c92ceef54bb08f7a8a178f6e553daa
size_kb: 1.16
---

# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the Jaeger project. ADRs document important architectural decisions made during the development of Jaeger, including the context, decision, and consequences of each choice.

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences. ADRs help teams understand why certain decisions were made and provide historical context for future contributors.

## ADRs in This Repository

- [ADR-001: Cassandra FindTraceIDs Duration Query Behavior](001-cassandra-find-traces-duration.md) - Explains why duration queries in the Cassandra spanstore use a separate code path and cannot be efficiently combined with other query parameters.
- [ADR-002: MCP Server Extension](002-mcp-server.md) - Design for implementing Model Context Protocol server as a Jaeger extension for LLM integration.
- [ADR-003: Lazy Storage Factory Initialization](003-lazy-storage-factory-initialization.md) - Comparative analysis of approaches to defer storage backend initialization until actually needed.

