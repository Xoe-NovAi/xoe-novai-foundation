import os
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLLBACK = ROOT / "scripts" / "phase5a-rollback.sh"


def make_fake_bin(bin_dir: Path):
    # sudo: execute the passed command (simple passthrough)
    (bin_dir / "sudo").write_text("""#!/usr/bin/env bash
# passthrough sudo used for tests
exec "$@"
""")

    # systemctl: emulate list-units and noop for stop/disable/daemon-reload
    (bin_dir / "systemctl").write_text("""#!/usr/bin/env bash
if [[ "$1" == "list-units" ]]; then
  # print a line containing xnai-zram so the script's grep succeeds
  echo "  xnai-zram.service loaded active running xnai-zram"
  exit 0
fi
# other commands just succeed
exit 0
""")

    # swapon --show -> print a line with zram0
    (bin_dir / "swapon").write_text("""#!/usr/bin/env bash
if [[ "$1" == "--show" ]]; then
  echo "/dev/zram0 none swap sw 0 0"
  exit 0
fi
exit 0
""")

    # swapoff -> noop
    (bin_dir / "swapoff").write_text("""#!/usr/bin/env bash
exit 0
""")

    # zramctl -> noop
    (bin_dir / "zramctl").write_text("""#!/usr/bin/env bash
exit 0
""")

    for p in bin_dir.iterdir():
        p.chmod(p.stat().st_mode | stat.S_IEXEC)


def test_phase5a_rollback_creates_backups_and_removes_files(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_fake_bin(bin_dir)

    # create fake target files that the rollback script will remove
    sysctl_file = tmp_path / "99-xnai-zram-tuning.conf"
    service_file = tmp_path / "xnai-zram.service"
    health_timer = tmp_path / "xnai-zram-health.timer"
    health_service = tmp_path / "xnai-zram-health.service"

    for f in (sysctl_file, service_file, health_timer, health_service):
        f.write_text("dummy")

    backup_dir = tmp_path / "backup"
    backup_dir.mkdir()

    env = os.environ.copy()
    # override script paths to point at our temp files
    env.update({
        "PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""),
        "XNAI_PHASE5A_BACKUP_DIR": str(backup_dir),
        "XNAI_SYSCTL_FILE": str(sysctl_file),
        "XNAI_SERVICE_FILE": str(service_file),
        "XNAI_HEALTH_TIMER": str(health_timer),
        "XNAI_HEALTH_SERVICE": str(health_service),
    })

    # run the rollback script
    completed = subprocess.run([str(ROLLBACK)], env=env, cwd=str(ROOT))
    assert completed.returncode == 0

    # original files should be removed
    assert not sysctl_file.exists()
    assert not service_file.exists()
    assert not health_timer.exists()
    assert not health_service.exists()

    # backups should exist in backup_dir
    backups = list(backup_dir.iterdir())
    assert any("sysctl" in p.name or p.name.endswith("99-xnai-zram-tuning.conf") for p in backups)
    assert any("xnai-zram" in p.name for p in backups)
