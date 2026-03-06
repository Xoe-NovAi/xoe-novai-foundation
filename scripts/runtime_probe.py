#!/usr/bin/env python3
"""
Runtime probe for Xoe-NovAi Foundation — outputs JSON summary + Prometheus textfile metrics.
Writes two files into --output-dir (default: monitoring/prometheus/textfile):
 - runtime_probe.json   (JSON state for RAG/agents)
 - runtime_probe.prom   (Prometheus textfile collector format)

Designed to be safe (read-only), robust if tools are missing, and easy for agents to parse.
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime


def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, text=True)
    except Exception:
        return ""


def have_cmd(name):
    return shutil.which(name) is not None


def get_cpu_cores():
    out = run("nproc --all")
    try:
        return int(out.strip())
    except Exception:
        return 0


def get_mem_total_bytes():
    out = run("/usr/bin/free -b 2>/dev/null || true")
    for line in out.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    return int(parts[1])
                except Exception:
                    return 0
    return 0


def probe_vulkan():
    result = {"present": False, "host_visible_count": 0, "device_local_count": 0}
    if not have_cmd("vulkaninfo"):
        return result
    out = run("vulkaninfo 2>/dev/null || true")
    if not out:
        return result
    result["present"] = True
    # crude counts: look for property flag names in memory type lines
    hv = out.count("VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT")
    dl = out.count("VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT")
    result["host_visible_count"] = hv
    result["device_local_count"] = dl
    return result


def probe_container_runtime():
    podman = have_cmd("podman")
    docker = have_cmd("docker")
    podman_info = run("podman info --format=json 2>/dev/null || true") if podman else ""
    docker_info = run("docker info --format '{{json .}}' 2>/dev/null || true") if docker else ""
    return {
        "podman_present": podman,
        "docker_present": docker,
        "podman_info_snippet": podman_info[:4096],
        "docker_info_snippet": docker_info[:4096],
    }


def write_prom(output_dir, data):
    path = f"{output_dir.rstrip('/')}/runtime_probe.prom"
    lines = []
    lines.append(f"# runtime_probe metrics — generated: {data['timestamp']}")
    lines.append(f"host_cpu_cores {data['host_cpu_cores']}")
    lines.append(f"host_mem_total_bytes {data['host_mem_total_bytes']}")
    lines.append(f"podman_present {1 if data['podman_present'] else 0}")
    lines.append(f"docker_present {1 if data['docker_present'] else 0}")
    vul = data.get('vulkan', {})
    lines.append(f"vulkan_present {1 if vul.get('present') else 0}")
    lines.append(f"vulkan_host_visible_memory_types_count {vul.get('host_visible_count',0)}")
    lines.append(f"vulkan_device_local_memory_types_count {vul.get('device_local_count',0)}")
    lines.append(f"runtime_probe_probe_success 1")
    try:
        with open(path, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        return path
    except Exception as e:
        print(f"ERROR: cannot write metrics to {path}: {e}", file=sys.stderr)
        return None


def write_json(output_dir, data):
    path = f"{output_dir.rstrip('/')}/runtime_probe.json"
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return path
    except Exception as e:
        print(f"ERROR: cannot write json to {path}: {e}", file=sys.stderr)
        return None


def main():
    p = argparse.ArgumentParser(description='Xoe-NovAi runtime probe (prom + json)')
    p.add_argument('--output-dir', '-o', default='monitoring/prometheus/textfile', help='Directory to write metrics and JSON')
    args = p.parse_args()

    cpu = get_cpu_cores()
    mem = get_mem_total_bytes()
    container = probe_container_runtime()
    vulkan = probe_vulkan()

    data = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'host_cpu_cores': cpu,
        'host_mem_total_bytes': mem,
        'podman_present': container['podman_present'],
        'docker_present': container['docker_present'],
        'vulkan': vulkan,
    }

    json_path = write_json(args.output_dir, data)
    prom_path = write_prom(args.output_dir, data)

    if json_path and prom_path:
        print(f"Wrote: {json_path}, {prom_path}")
        sys.exit(0)
    else:
        print("Probe failed to write outputs", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
