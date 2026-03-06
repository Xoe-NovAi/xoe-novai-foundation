import json
import os
import subprocess
import sys

def test_runtime_probe_writes_prom_and_json(tmp_path):
    outdir = tmp_path
    script = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'runtime_probe.py')
    script = os.path.normpath(script)
    cmd = [sys.executable, script, '--output-dir', str(outdir)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    prom = outdir / 'runtime_probe.prom'
    j = outdir / 'runtime_probe.json'
    assert prom.exists(), 'prom file missing'
    assert j.exists(), 'json file missing'
    text = prom.read_text()
    assert 'host_cpu_cores' in text
    assert 'runtime_probe_probe_success' in text
    # validate JSON keys
    data = json.loads(j.read_text())
    assert 'host_cpu_cores' in data
    assert 'host_mem_total_bytes' in data
