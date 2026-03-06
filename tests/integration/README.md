# Phase 4.1 Integration Tests

Comprehensive integration tests for the Xoe-NovAi Foundation stack, focusing on service discovery, gateway routing, database connectivity, and Rootless Podman network isolation.

## Overview

This integration test suite validates:

- **Service Discovery**: Consul service registration, health checks, and mesh connectivity
- **Gateway Routing**: API Gateway routing rules, load balancing, security headers, and CORS
- **Database Connectivity**: PostgreSQL connection pooling, Redis cache connectivity, and failover scenarios
- **Rootless Podman Network Isolation**: Container network security and isolation
- **Hardware Optimization**: Ryzen 7 5700U / Vega 8 compatibility and performance
- **Streaming Functionality**: SSE and WebSocket support
- **Performance Metrics**: Response times and memory usage validation

## Prerequisites

### System Requirements
- **CPU**: Ryzen 7 5700U (recommended) or equivalent
- **GPU**: Vega 8 with Vulkan support (recommended)
- **Memory**: 16GB+ RAM
- **Storage**: 50GB+ available space
- **OS**: Linux with Podman support

### Software Requirements
- **Podman**: Rootless container runtime
- **Python 3.12+**: With required dependencies
- **Vulkan**: GPU acceleration support
- **zRAM**: 2-tier configuration (lz4 + zstd)
- **Docker Compose**: For service orchestration

### Python Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-json-report
pip install httpx fastapi redis psycopg2-binary
pip install docker psutil requests
```

## Test Structure

```
tests/integration/
├── README.md                           # This file
├── conftest.py                         # Pytest configuration and fixtures
├── test_fixtures.py                    # Test data and mock services
├── test_service_discovery.py           # Service discovery tests
├── test_gateway_routing.py             # Gateway routing tests
├── test_db_connectivity.py             # Database connectivity tests
├── run_integration_tests.py            # Main test runner
└── __pycache__/                        # Python cache files
```

## Running Tests

### Option 1: Run All Integration Tests
```bash
# Run the complete integration test suite
python tests/integration/run_integration_tests.py
```

### Option 2: Run Individual Test Categories
```bash
# Service discovery tests only
pytest tests/integration/test_service_discovery.py -v

# Gateway routing tests only
pytest tests/integration/test_gateway_routing.py -v

# Database connectivity tests only
pytest tests/integration/test_db_connectivity.py -v
```

### Option 3: Run with Pytest Directly
```bash
# Run all integration tests with detailed output
pytest tests/integration/ -v --tb=short

# Run with JSON report generation
pytest tests/integration/ -v --json-report --json-report-file=integration_report.json

# Run specific test markers
pytest tests/integration/ -v -m "integration"
pytest tests/integration/ -v -m "hardware"
pytest tests/integration/ -v -m "network"
```

## Test Configuration

### Environment Variables
Set these environment variables before running tests:

```bash
export TEST_NETWORK_NAME="xnai_network"
export TEST_TIMEOUT=300
export TEST_RETRY_INTERVAL=5
export HARDWARE_OPTIMIZATION="ryzen_vega"
```

### Test Services
The tests expect these services to be available:

- **RAG API**: http://localhost:8000
- **Chainlit**: http://localhost:8001
- **Vikunja**: http://localhost:9000
- **MkDocs**: http://localhost:8002
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432
- **Caddy Gateway**: http://localhost:80

### Podman Configuration
Ensure Rootless Podman is properly configured:

```bash
# Check if running rootless
whoami  # Should not be root

# Verify Podman version
podman --version

# Check network configuration
podman network ls
```

## Test Categories

### 1. Hardware Compatibility Tests
- CPU model verification (Ryzen 7 5700U)
- GPU and Vulkan support (Vega 8)
- zRAM configuration (2-tier: lz4 + zstd)
- Memory optimization validation

### 2. Network Isolation Tests
- Rootless Podman verification
- Network namespace isolation
- Container-to-container communication
- External network access
- Security boundary validation

### 3. Service Discovery Tests
- Consul service registration
- Health check functionality
- Service mesh connectivity
- Failover scenarios
- Load testing under stress

### 4. Gateway Routing Tests
- API Gateway routing rules
- Request/response handling
- Load balancing across services
- Security headers and CORS
- Rate limiting and authentication

### 5. Database Connectivity Tests
- PostgreSQL connection pooling
- Redis cache operations
- Database failover scenarios
- Connection limits and timeouts
- Transaction handling

### 6. Streaming Functionality Tests
- Server-Sent Events (SSE)
- WebSocket connections
- Real-time data streaming
- Connection persistence

### 7. Performance Tests
- Response time validation (<200ms target)
- Memory usage monitoring (<6GB target)
- Throughput measurement
- Resource utilization

## Expected Results

### Success Criteria
- ✅ All hardware compatibility tests pass
- ✅ Rootless Podman network isolation verified
- ✅ Service discovery tests: 100% success rate
- ✅ Gateway routing tests: 100% success rate
- ✅ Database connectivity tests: 100% success rate
- ✅ Response times: <200ms average
- ✅ Memory usage: <6GB total
- ✅ All services accessible through gateway

### Performance Targets
- **Latency**: <200ms for API responses
- **Memory**: <6GB total system usage
- **CPU**: Optimized for Ryzen 7 5700U
- **GPU**: Vulkan acceleration enabled
- **Network**: Secure Rootless Podman isolation

## Troubleshooting

### Common Issues

#### Podman Not Available
```bash
# Install Podman
sudo apt install podman podman-compose

# Configure rootless mode
sudo usermod -aG podman $USER
newgrp podman
```

#### Services Not Running
```bash
# Start all services
podman-compose up -d

# Check service status
podman ps

# View logs
podman logs <container_name>
```

#### Network Issues
```bash
# Check network configuration
podman network ls
podman network inspect xnai_network

# Test connectivity
podman exec <container> ping <other_container>
```

#### Hardware Detection Issues
```bash
# Check CPU info
lscpu

# Check GPU and Vulkan
vulkaninfo --summary

# Check zRAM
zramctl
```

### Debug Mode
Run tests in debug mode for detailed output:

```bash
# Enable debug logging
export DEBUG=1

# Run with verbose output
python tests/integration/run_integration_tests.py --debug
```

## Test Reports

### Generated Files
After running tests, these files are generated:

- `integration_test_report.json` - Detailed JSON report
- `INTEGRATION_TEST_SUMMARY.md` - Human-readable summary
- `integration_test.log` - Detailed execution log
- `integration_report.json` - Pytest JSON report

### Report Analysis
Review the generated reports to:

1. **Identify failures**: Check for ❌ critical failures
2. **Review warnings**: Address ⚠️ warnings where possible
3. **Monitor performance**: Verify response times and memory usage
4. **Validate isolation**: Confirm network security measures

## Continuous Integration

### GitHub Actions Integration
Add this to your `.github/workflows/integration-tests.yml`:

```yaml
name: Integration Tests
on: [push, pull_request]
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run integration tests
        run: python tests/integration/run_integration_tests.py
```

### Docker Integration
Run tests in a containerized environment:

```bash
# Build test container
docker build -t xnai-integration-tests .

# Run tests
docker run --rm -v /var/run/podman:/var/run/podman \
  -v /tmp:/tmp xnai-integration-tests
```

## Contributing

### Adding New Tests
1. Create test file in `tests/integration/`
2. Follow existing test patterns
3. Add appropriate pytest markers
4. Update this README with new test description
5. Test locally before submitting

### Test Best Practices
- Use async/await for I/O operations
- Implement proper error handling
- Include comprehensive assertions
- Add performance monitoring
- Document test purpose and expected outcomes

## Support

For issues with integration tests:

1. Check the troubleshooting section above
2. Review generated log files
3. Verify system prerequisites
4. Ensure services are running
5. Check network connectivity

## License

This test suite is part of the Xoe-NovAi Foundation project and follows the same license terms.