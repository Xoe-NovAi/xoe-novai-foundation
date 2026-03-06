# Phase‑5A Quickstart — zRAM Health & Validation

This quickstart will walk a new operator through the staging validation for Phase‑5A.

Prerequisites
- Staging host with `zramctl` installed
- A self-hosted GitHub Actions runner labeled `self-hosted,linux,privileged` (optional for CI)

Steps
1. Baseline collection
  - mkdir -p /tmp/phase5a-baseline
  - free -h > /tmp/phase5a-baseline/memory-start.txt
  - sysctl vm.swappiness vm.page-cluster > /tmp/phase5a-baseline/kernel-params-start.txt

2. Apply Phase‑5A (Ansible)
  - ansible-playbook internal_docs/ansible/playbooks/phase5a_apply.yml -i inventory --limit <staging-host>

3. Validate locally
  - sudo python3 scripts/validate-phase-5a.py

4. Run staging stress test
  - sudo python3 scripts/phase-5a-stress-test.py --staging --duration 300 --workers 3

5. Check metrics
  - tail -n +1 /var/lib/node_exporter/textfile_collector/xnai_zram.prom
  - Open Grafana dashboard: `xnai_zram_dashboard` (UID: xnai-zram-health)

6. Rollback (if needed)
  - ansible-playbook internal_docs/ansible/playbooks/phase5a_rollback.yml -i inventory --limit <staging-host>

Troubleshooting
- If zramctl shows no device: check `systemctl status xnai-zram.service` and `journalctl -u xnai-zram.service -n 200`
- If metrics missing: verify `node_exporter` textfile collector dir ownership and file permissions

