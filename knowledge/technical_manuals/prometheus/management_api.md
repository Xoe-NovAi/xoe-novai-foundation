---
title: Management Api
service: prometheus
source_urls: ["/tmp/tmp3costqih/repo/docs/management_api.md"]
scraped_at: 2026-02-17T00:22:07.514256
content_hash: a35c19a065c3b98bc2f4129a4159f8962c08744a274f396b1061d6c357e6069a
size_kb: 1.01
---

---
title: Management API
sort_rank: 8
---

Prometheus provides a set of management APIs to facilitate automation and integration.


## Health check

```
GET /-/healthy
HEAD /-/healthy
```

This endpoint always returns 200 and should be used to check Prometheus health.


## Readiness check

```
GET /-/ready
HEAD /-/ready
```

This endpoint returns 200 when Prometheus is ready to serve traffic (i.e. respond to queries).


## Reload

```
PUT  /-/reload
POST /-/reload
```

This endpoint triggers a reload of the Prometheus configuration and rule files. It's disabled by default and can be enabled via the `--web.enable-lifecycle` flag.

Alternatively, a configuration reload can be triggered by sending a `SIGHUP` to the Prometheus process.


## Quit

```
PUT  /-/quit
POST /-/quit
```

This endpoint triggers a graceful shutdown of Prometheus. It's disabled by default and can be enabled via the `--web.enable-lifecycle` flag.

Alternatively, a graceful shutdown can be triggered by sending a `SIGTERM` to the Prometheus process.
