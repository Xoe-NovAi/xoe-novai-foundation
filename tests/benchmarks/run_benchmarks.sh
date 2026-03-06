#!/bin/bash
# Database Benchmarking Suite Runner
# Runs all benchmarks and generates comprehensive reports

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Print header
print_header() {
    echo ""
    echo "================================================================================"
    echo "$1"
    echo "================================================================================"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        exit 1
    fi
    log_success "Python 3 found: $(python3 --version)"
    
    # Check Docker/Podman for services
    if ! command -v docker &> /dev/null && ! command -v podman &> /dev/null; then
        log_warn "Docker/Podman not found - assuming services are already running"
    else
        log_success "Container runtime found"
    fi
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"
    
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        python3 -m pip install -q --upgrade pip
        python3 -m pip install -q -r "$SCRIPT_DIR/requirements.txt"
        log_success "Dependencies installed"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
}

# Check database connectivity
check_database_connectivity() {
    print_header "Checking Database Connectivity"
    
    # PostgreSQL
    log_info "Checking PostgreSQL..."
    if python3 -c "
import psycopg
try:
    conn = psycopg.connect(
        host='${POSTGRES_HOST:-localhost}',
        port=${POSTGRES_PORT:-5432},
        user='${POSTGRES_USER:-postgres}',
        password='${POSTGRES_PASSWORD:-postgres}',
        dbname='${POSTGRES_DB:-xnai}',
        timeout=5
    )
    conn.close()
    print('✓ PostgreSQL connected')
except Exception as e:
    print(f'✗ PostgreSQL failed: {e}')
    exit(1)
" 2>/dev/null; then
        log_success "PostgreSQL is accessible"
    else
        log_warn "PostgreSQL not accessible at ${POSTGRES_HOST:-localhost}:${POSTGRES_PORT:-5432}"
    fi
    
    # Redis
    log_info "Checking Redis..."
    if python3 -c "
import redis
try:
    r = redis.Redis(
        host='${REDIS_HOST:-localhost}',
        port=${REDIS_PORT:-6379},
        password='${REDIS_PASSWORD:-}' if '${REDIS_PASSWORD:-}' else None,
        socket_connect_timeout=5
    )
    r.ping()
    print('✓ Redis connected')
except Exception as e:
    print(f'✗ Redis failed: {e}')
    exit(1)
" 2>/dev/null; then
        log_success "Redis is accessible"
    else
        log_warn "Redis not accessible at ${REDIS_HOST:-localhost}:${REDIS_PORT:-6379}"
    fi
    
    # Qdrant
    log_info "Checking Qdrant..."
    if python3 -c "
from qdrant_client.async_client import AsyncQdrantClient
import asyncio
try:
    async def check():
        client = AsyncQdrantClient(
            host='${QDRANT_HOST:-localhost}',
            port=${QDRANT_PORT:-6333}
        )
        try:
            await client.get_collections()
            return True
        except:
            return False
        finally:
            await client.close()
    result = asyncio.run(check())
    if result:
        print('✓ Qdrant connected')
    else:
        raise Exception('Connection failed')
except Exception as e:
    print(f'✗ Qdrant failed: {e}')
    exit(1)
" 2>/dev/null; then
        log_success "Qdrant is accessible"
    else
        log_warn "Qdrant not accessible at ${QDRANT_HOST:-localhost}:${QDRANT_PORT:-6333}"
    fi
}

# Run database benchmarks
run_database_benchmarks() {
    print_header "Running Database Benchmarks"
    
    log_info "Starting database benchmarks (this may take 5-10 minutes)..."
    
    if python3 "$SCRIPT_DIR/database_benchmarks.py" 2>&1 | tee "$RESULTS_DIR/database_benchmarks_${TIMESTAMP}.log"; then
        log_success "Database benchmarks completed"
    else
        log_error "Database benchmarks failed"
        return 1
    fi
}

# Run combined system benchmarks
run_combined_benchmarks() {
    print_header "Running Combined System Benchmarks"
    
    log_info "Starting combined system benchmarks..."
    
    if python3 "$SCRIPT_DIR/combined_benchmarks.py" 2>&1 | tee "$RESULTS_DIR/combined_benchmarks_${TIMESTAMP}.log"; then
        log_success "Combined benchmarks completed"
    else
        log_error "Combined benchmarks failed"
        return 1
    fi
}

# Generate summary report
generate_summary_report() {
    print_header "Generating Summary Report"
    
    log_info "Generating benchmark summary..."
    
    python3 <<'EOF'
import json
import sys
from pathlib import Path
from datetime import datetime

results_dir = Path("benchmarks")
db_results = results_dir / "database_benchmark_results.json"
combined_results = results_dir / "combined_benchmark_results.json"

if not db_results.exists() or not combined_results.exists():
    print("Results files not found")
    sys.exit(1)

with open(db_results) as f:
    db_data = json.load(f)

with open(combined_results) as f:
    combined_data = json.load(f)

# Generate summary
summary = {
    "timestamp": datetime.now().isoformat(),
    "summary": {
        "PostgreSQL": {},
        "Redis": {},
        "Qdrant": {},
        "Combined": {}
    }
}

# PostgreSQL summary
for name, stats in db_data.get("PostgreSQL", {}).items():
    if stats:
        summary["summary"]["PostgreSQL"][name] = {
            "p50": f"{stats.get('p50', 0):.2f}ms",
            "p95": f"{stats.get('p95', 0):.2f}ms",
            "p99": f"{stats.get('p99', 0):.2f}ms",
            "mean": f"{stats.get('mean', 0):.2f}ms"
        }

# Redis summary
for name, stats in db_data.get("Redis", {}).items():
    if stats:
        summary["summary"]["Redis"][name] = {
            "p50": f"{stats.get('p50', 0):.2f}ms",
            "p95": f"{stats.get('p95', 0):.2f}ms",
            "p99": f"{stats.get('p99', 0):.2f}ms",
            "mean": f"{stats.get('mean', 0):.2f}ms"
        }

# Qdrant summary
for name, stats in db_data.get("Qdrant", {}).items():
    if stats:
        summary["summary"]["Qdrant"][name] = {
            "p50": f"{stats.get('p50', 0):.2f}ms",
            "p95": f"{stats.get('p95', 0):.2f}ms",
            "p99": f"{stats.get('p99', 0):.2f}ms",
            "mean": f"{stats.get('mean', 0):.2f}ms"
        }

# Combined summary
for name, stats in combined_data.get("combined_system", {}).items():
    if stats:
        summary["summary"]["Combined"][name] = {
            "p50": f"{stats.get('p50', 0):.2f}ms",
            "p95": f"{stats.get('p95', 0):.2f}ms",
            "p99": f"{stats.get('p99', 0):.2f}ms",
            "mean": f"{stats.get('mean', 0):.2f}ms"
        }

# Save summary
with open(results_dir / "benchmark_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("Summary report generated: benchmarks/benchmark_summary.json")

# Print summary to console
print("\n" + "="*60)
print("BENCHMARK RESULTS SUMMARY")
print("="*60)

for system, tests in summary["summary"].items():
    print(f"\n{system}:")
    for test_name, metrics in tests.items():
        print(f"  {test_name}: p50={metrics['p50']}, p95={metrics['p95']}, p99={metrics['p99']}")

EOF
}

# Cleanup
cleanup() {
    log_info "Cleaning up temporary files..."
    # Cleanup is optional - uncomment if needed
    # rm -rf /tmp/benchmark_*
}

# Main execution
main() {
    print_header "XNAi Foundation Database Benchmarking Suite"
    log_info "Timestamp: $(date)"
    log_info "Results directory: $RESULTS_DIR"
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Run checks
    check_prerequisites
    install_dependencies
    check_database_connectivity
    
    # Run benchmarks
    if run_database_benchmarks; then
        if run_combined_benchmarks; then
            generate_summary_report
            log_success "All benchmarks completed successfully!"
        else
            log_error "Combined benchmarks failed"
            exit 1
        fi
    else
        log_error "Database benchmarks failed"
        exit 1
    fi
    
    cleanup
    
    print_header "Benchmark Execution Complete"
    log_success "Results saved to: $RESULTS_DIR"
    log_info "Documentation: benchmarks/PERFORMANCE-BASELINES.md"
}

# Run main
main "$@"
