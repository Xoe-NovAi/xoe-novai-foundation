#!/bin/bash
set -a
source "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/.env"
set +a
podman-compose -f "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/infra/docker/docker-compose.yml" up -d
