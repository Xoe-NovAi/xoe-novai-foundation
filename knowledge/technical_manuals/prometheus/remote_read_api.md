---
title: Remote Read Api
service: prometheus
source_urls: ["/tmp/tmp3costqih/repo/docs/querying/remote_read_api.md"]
scraped_at: 2026-02-17T00:22:07.518431
content_hash: 78a3402906b53e4e180e168eefd2a6b6f97cbbff52f8391065793c2175c18913
size_kb: 0.98
---

---
title: Remote Read API
sort_rank: 7
---

NOTE: This is not currently considered part of the stable API and is subject to change even between non-major version releases of Prometheus.

This API provides data read functionality from Prometheus. This interface expects [snappy](https://github.com/google/snappy) compression.
The API definition is located [here](https://github.com/prometheus/prometheus/blob/main/prompb/remote.proto).
Protobuf definitions are also available on [buf.build](https://buf.build/prometheus/prometheus/docs/main:prometheus#prometheus.ReadRequest).

Request are made to the following endpoint.
```
/api/v1/read
```

## Samples

This returns a message that includes a list of raw samples matching the
requested query.

## Streamed Chunks

These streamed chunks utilize an XOR algorithm inspired by the [Gorilla](http://www.vldb.org/pvldb/vol8/p1816-teller.pdf)
compression to encode the chunks. However, it provides resolution to the millisecond instead of to the second.
