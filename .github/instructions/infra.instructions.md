---
applyTo: ["scripts/**/*.sh", "docker-compose.yml", "Dockerfile*"]
---

# Infrastructure Instructions

Follow these standards for all Ops/Infra tasks:
1.  **Rootless Podman**: No rootful Docker patterns.
2.  **AMD Vega Tuning**: Use `64-wide` wavefront size for Vulkan shaders.
3.  **zRAM Standard**: Always use the 2-tier (lz4 + zstd) standard.
4.  **Zero-Telemetry**: No external API calls during build or runtime without explicit flags.
