#!/bin/bash
# scripts/generate_tls_certs.sh
# Generate self-signed certificates for intra-stack Redis TLS

set -e

TLS_DIR="infra/docker/tls"
mkdir -p "$TLS_DIR"

echo "🔐 Generating CA and Redis certificates in $TLS_DIR..."

# 1. Generate CA
openssl genrsa -out "$TLS_DIR/ca.key" 4096
openssl req -x509 -new -nodes -sha256 -key "$TLS_DIR/ca.key" -days 3650 -out "$TLS_DIR/ca.crt" -subj "/CN=XNAi-Internal-CA"

# 2. Generate Redis Server Key & Cert
openssl genrsa -out "$TLS_DIR/redis.key" 2048
openssl req -new -sha256 -key "$TLS_DIR/redis.key" -out "$TLS_DIR/redis.csr" -subj "/CN=redis"

# 3. Sign the Redis Cert with our CA
# We add 'redis' and 'localhost' as Subject Alternative Names (SAN) for compatibility
cat > "$TLS_DIR/redis.ext" << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = redis
DNS.2 = localhost
IP.1 = 127.0.0.1
EOF

openssl x509 -req -in "$TLS_DIR/redis.csr" -CA "$TLS_DIR/ca.crt" -CAkey "$TLS_DIR/ca.key" -CAcreateserial \
    -out "$TLS_DIR/redis.crt" -days 365 -sha256 -extfile "$TLS_DIR/redis.ext"

# 4. Set permissions
chmod 644 "$TLS_DIR/ca.crt" "$TLS_DIR/redis.crt"
chmod 600 "$TLS_DIR/ca.key" "$TLS_DIR/redis.key"

# 5. Clean up temporary files
rm "$TLS_DIR/redis.csr" "$TLS_DIR/redis.ext"

# 6. Update .gitignore if not already there
if ! grep -q "infra/docker/tls/" .gitignore; then
    echo -e "\n# Redis TLS Certificates\ninfra/docker/tls/" >> .gitignore
    echo "✅ Updated .gitignore"
fi

echo "✨ TLS Certificates generated successfully."
