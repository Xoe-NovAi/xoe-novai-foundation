---
title: Ctn Build
service: docker
source_urls: ["/tmp/tmpk3lj64bi/repo/docs/contributing/ctn-build.md"]
scraped_at: 2026-02-17T00:21:43.255805
content_hash: 380917952809a29533437812fbd90df2a4bddedeed66da4cff70b164d6ab9c1c
size_kb: 1.75
---

The `Dockerfile` supports building and cross compiling docker daemon and extra
tools using [Docker Buildx](https://github.com/docker/buildx) and [BuildKit](https://github.com/moby/buildkit).
A [bake definition](https://docs.docker.com/build/bake/reference/) named
`docker-bake.hcl` is in place to ease the build process.

Section [development container](set-up-dev-env.md#work-with-a-development-container)
describes how to develop and compile your changes in a Linux container. You can also build
and cross-compile the binaries.

```shell
# build binaries for the current host platform
# output to ./bundles/binary-daemon by default
docker buildx bake
# or
docker buildx bake binary

# build binaries for the current host platform
# output to ./bin
DESTDIR=./bin docker buildx bake

# build dynamically linked binaries
# output to ./bundles/dynbinary-daemon by default
DOCKER_STATIC=0 docker buildx bake
# or
docker buildx bake dynbinary

# build binaries for all supported platforms
docker buildx bake binary-cross

# build binaries for a specific platform
docker buildx bake --set *.platform=linux/arm64

# build "complete" binaries (including containerd, runc, vpnkit, etc.)
docker buildx bake all

# build "complete" binaries for all supported platforms
docker buildx bake all-cross

# build non-runnable image wrapping "complete" binaries
# useful for use with undock and sharing via a registry
docker buildx bake bin-image

# build non-runnable image wrapping "complete" binaries, with custom tag
docker buildx bake bin-image --set "*.tags=foo/moby-bin:latest"

# build non-runnable image wrapping "complete" binaries for all supported platforms
# multi-platform images must be directly pushed to a registry
docker buildx bake bin-image-cross --set "*.tags=foo/moby-bin:latest" --push
```
