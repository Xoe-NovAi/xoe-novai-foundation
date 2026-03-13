#!/usr/bin/env python3
"""
Phase 5A Stress Test (safe mode)
- Supports --staging (default) to run an incremental ramp
- Use --confirm-prod to run full stress (use only in staging or with approval)
- Safety: aborts if CPU or memory exceed thresholds
"""

import argparse
import subprocess
import time
import sys
import os

try:
    import psutil
    PSUTIL=True
except Exception:
    PSUTIL=False

from datetime import datetime


def get_cpu_percent():
    if PSUTIL:
        return psutil.cpu_percent(interval=0.5)
    # fallback: parse /proc/stat (very rough)
    return 0.0


def get_mem_percent():
    if PSUTIL:
        return psutil.virtual_memory().percent
    # fallback: use free
    out = subprocess.run(['free','-m'], capture_output=True, text=True)
    lines = out.stdout.splitlines()
    if len(lines) >= 2:
        parts = lines[1].split()
        if len(parts) >= 3:
            total = float(parts[1]); used = float(parts[2])
            return used/total*100.0
    return 0.0


def run_memory_workers(workers, allocation_mb):
    procs = []
    for i in range(workers):
        # use stress-ng if available
        if shutil.which('stress-ng'):
            cmd = ['stress-ng','--vm','1','--vm-bytes','%dM' % allocation_mb,'--vm-keep','--timeout','300s']
            p = subprocess.Popen(cmd)
            procs.append(p)
        else:
            # fallback: spawn Python subprocess that allocates memory
            p = subprocess.Popen([sys.executable, '-c', (
                'a=[bytearray(%d) for _ in range(1)]; import time; time.sleep(300)'
            ) % (allocation_mb*1024*1024)])
            procs.append(p)
    return procs


def monitor_and_abort(max_cpu, max_mem):
    cpu = get_cpu_percent()
    mem = get_mem_percent()
    if cpu > max_cpu or mem > max_mem:
        print(f"Abort: CPU {cpu:.1f}% > {max_cpu}% or MEM {mem:.1f}% > {max_mem}%")
        return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Phase 5A stress test (safe)')
    parser.add_argument('--duration', type=int, default=600, help='Total duration in seconds')
    parser.add_argument('--workers', type=int, default=5, help='Requested workers (5x default)')
    parser.add_argument('--staging', action='store_true', default=True, help='Use staged ramp (default)')
    parser.add_argument('--ramp-steps', type=int, default=3, help='Number of ramp steps for staging')
    parser.add_argument('--max-cpu', type=int, default=85, help='Abort if CPU% exceeds this')
    parser.add_argument('--max-mem', type=int, default=92, help='Abort if memory% exceeds this')
    parser.add_argument('--confirm-prod', action='store_true', help='Allow full production intensity')
    parser.add_argument('--baseline-only', action='store_true', help='Collect baseline and exit')
    args = parser.parse_args()

    import shutil

    print('\nPHASE 5A STRESS TEST (safe mode)')
    print(f"Start: {datetime.now().isoformat()} | duration={args.duration}s | workers={args.workers}")

    if args.baseline_only:
        print('Collecting baseline (see /tmp/phase5a-baseline/)')
        subprocess.run(['bash','-c','free -h > /tmp/phase5a-baseline/memory-start.txt; sysctl vm.swappiness vm.page-cluster > /tmp/phase5a-baseline/kernel-params-start.txt'])
        sys.exit(0)

    if not args.confirm_prod and args.staging:
        # reduce intensity for staging
        target_workers = max(1, args.workers // 2)
        print(f"Staging mode: running ramp to {target_workers} workers (use --confirm-prod for full load)")
    else:
        target_workers = args.workers

    # Ramp strategy
    steps = args.ramp_steps if args.staging else 1
    step_duration = max(10, args.duration // max(1,steps))
    workers_per_step = [ max(1, int(target_workers * ((i+1)/steps))) for i in range(steps) ]

    print(f"Ramp steps: {steps} -> workers per step: {workers_per_step}")

    allocation_mb = 256  # per-worker allocation (tunable)
    procs = []
    try:
        for idx, w in enumerate(workers_per_step):
            print(f"Step {idx+1}/{steps}: starting {w} workers for {step_duration}s")
            # start workers
            for p in run_memory_workers(w, allocation_mb):
                procs.append(p)
            # monitor during step
            start = time.time()
            while time.time() - start < step_duration:
                if monitor_and_abort(args.max_cpu, args.max_mem):
                    raise RuntimeError('Safety threshold exceeded')
                time.sleep(2)
            print(f"Step {idx+1} complete")
        print('Holding load until end of duration...')
        remaining = args.duration - steps*step_duration
        if remaining > 0:
            start = time.time()
            while time.time() - start < remaining:
                if monitor_and_abort(args.max_cpu, args.max_mem):
                    raise RuntimeError('Safety threshold exceeded')
                time.sleep(2)
        print('Stress window complete')
    except Exception as e:
        print(f'Error during stress test: {e}')
    finally:
        print('Cleaning up workers...')
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass
        time.sleep(1)

    print('Collecting final zRAM stats...')
    subprocess.run(['bash','-c','zramctl || true'])
    print('Done')
