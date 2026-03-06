import os
import stat
import subprocess
import tempfile

SCRIPT = os.path.abspath('scripts/zram-health-check.sh')


def make_fake_zramctl(output_text, dst_dir):
    p = os.path.join(dst_dir, 'zramctl')
    with open(p, 'w') as f:
        f.write('#!/usr/bin/env bash\n')
        f.write('cat <<"EOF"\n')
        f.write(output_text + '\n')
        f.write('EOF\n')
    os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR)
    return p


def test_health_check_writes_prom(tmp_path, monkeypatch):
    # Create writable textfile collector dir
    outdir = tmp_path / 'textfile_collector'
    outdir.mkdir()

    # Prepare fake zramctl output (header + one device line)
    zram_output = 'DATA COMPR TOTAL ALGORITHM STREAMS\n2.0G 1.0G 2.0G zstd 4'

    # Create a fake zramctl and ensure PATH picks it up
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    fake = make_fake_zramctl(zram_output, str(bin_dir))

    env = os.environ.copy()
    env['PATH'] = str(bin_dir) + os.pathsep + env.get('PATH', '')
    env['XNAI_ZRAM_OUTPUT_DIR'] = str(outdir)

    # Run the health-check script
    subprocess.run([SCRIPT], check=True, env=env)

    prom = outdir / 'xnai_zram.prom'
    assert prom.exists(), 'Prometheus metrics file not written'
    content = prom.read_text()
    assert 'xnai_zram_compression_ratio' in content
    assert 'xnai_zram_used_bytes' in content
