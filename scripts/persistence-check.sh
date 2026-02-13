#!/usr/bin/env bash
# persistence-check.sh — verify Phase 5A config persisted after reboot

sleep 5

OK=0
ERR=1

if grep -q "vm.swappiness = 180" /etc/sysctl.d/99-xnai-zram-tuning.conf 2>/dev/null; then
  echo "sysctl file OK"
else
  echo "sysctl file MISSING or incorrect"
  exit $ERR
fi

if systemctl is-enabled xnai-zram.service &>/dev/null; then
  echo "xnai-zram.service enabled"
else
  echo "xnai-zram.service NOT enabled"
  exit $ERR
fi

if zramctl | grep -q zram0 2>/dev/null; then
  echo "zram0 active"
else
  echo "zram0 NOT active"
  exit $ERR
fi

echo "All persistence checks passed"
exit $OK
