#!/bin/bash

echo "🔍 Vikunja Pre-Deployment Checklist"
echo "======================================"

# 1. Directories exist
[ -d data/vikunja/db ] && echo "✅ data/vikunja/db exists" || echo "❌ MISSING: data/vikunja/db"
[ -d data/vikunja/files ] && echo "✅ data/vikunja/files exists" || echo "❌ MISSING: data/vikunja/files"
[ -d config ] && echo "✅ config/ exists" || echo "❌ MISSING: config/"
[ -d secrets ] && echo "✅ secrets/ exists" || echo "❌ MISSING: secrets/"

# 2. Configuration files exist
[ -f config/postgres.conf ] && echo "✅ config/postgres.conf exists" || echo "❌ MISSING: config/postgres.conf"
[ -f config/vikunja-config.yaml ] && echo "✅ config/vikunja-config.yaml exists" || echo "❌ MISSING: config/vikunja-config.yaml"

# 3. Secret files exist
[ -f secrets/redis_password.txt ] && echo "✅ secrets/redis_password.txt exists" || echo "❌ MISSING: secrets/redis_password.txt"
[ -f secrets/vikunja_db_password.txt ] && echo "✅ secrets/vikunja_db_password.txt exists" || echo "❌ MISSING: secrets/vikunja_db_password.txt"
[ -f secrets/vikunja_jwt_secret.txt ] && echo "✅ secrets/vikunja_jwt_secret.txt exists" || echo "❌ MISSING: secrets/vikunja_jwt_secret.txt"

# 4. Podman secrets created
podman secret list | grep -q "redis_password" && echo "✅ Podman secret: redis_password" || echo "❌ MISSING: Podman secret redis_password"
podman secret list | grep -q "vikunja_db_password" && echo "✅ Podman secret: vikunja_db_password" || echo "❌ MISSING: Podman secret vikunja_db_password"
podman secret list | grep -q "vikunja_jwt_secret" && echo "✅ Podman secret: vikunja_jwt_secret" || echo "❌ MISSING: Podman secret vikunja_jwt_secret"

# 5. Permissions set correctly
stat data/vikunja/db | grep -q "700" && echo "✅ data/vikunja/db has 700 permissions" || echo "⚠️  data/vikunja/db permissions not 700"
stat config/postgres.conf | grep -q "644" && echo "✅ config/postgres.conf is readable" || echo "⚠️  config/postgres.conf permissions issue"

# 6. Podman version check
PODMAN_VER=$(podman --version | grep -oP '(?<=version\s)\d+' | head -1)
[ "$PODMAN_VER" -ge 4 ] && echo "✅ Podman version ≥ 4.0" || echo "❌ FAIL: Podman version < 4.0"

# 7. Disk space check
DISK_FREE=$(df $(pwd) | awk 'NR==2 {print $4}')  # in KB
[ "$DISK_FREE" -gt 10485760 ] && echo "✅ At least 10GB free" || echo "❌ FAIL: Less than 10GB free"

# 8. .env file sourced
[ -f .env ] && echo "✅ .env exists" || echo "⚠️  .env not found (may be OK if in shell)"

echo ""
echo "Pre-flight check complete!"
