#!/usr/bin/env bash
# TEMPLATE: Provision & register a GitHub self-hosted runner (edit before use)
# Usage: sudo bash provision-runner-template.sh <GH_ORG> <GH_REPO> <RUNNER_LABELS>

set -euo pipefail
GH_ORG="$1"
GH_REPO="$2"
LABELS="$3"  # e.g. "self-hosted,linux,privileged"

if [ -z "$GH_ORG" ] || [ -z "$GH_REPO" ]; then
  echo "Usage: $0 <GH_ORG> <GH_REPO> <LABELS>"
  exit 2
fi

# ensure prerequisites
apt update && apt install -y curl jq git build-essential

# create unprivileged user
useradd -m -s /bin/bash actions-runner || true
RUNNER_HOME=/home/actions-runner
mkdir -p "$RUNNER_HOME" && chown $(whoami): "$RUNNER_HOME"
cd "$RUNNER_HOME"

# download latest runner (change version if needed)
RUNNER_URL="https://github.com/actions/runner/releases/latest/download/actions-runner-linux-x64.tar.gz"
curl -fsSL -o actions-runner.tar.gz "$RUNNER_URL"
tar xzf actions-runner.tar.gz

# NOTE: get registration token from GitHub UI: Settings -> Actions -> Runners -> New self-hosted runner
# then run the ./config.sh command below with the provided token. Do NOT commit the token.

# example (replace TOKEN and URL):
# ./config.sh --url https://github.com/${GH_ORG}/${GH_REPO} --token <TOKEN> --labels "$LABELS"

# install service
# sudo ./svc.sh install
# sudo ./svc.sh start

# For security: add sudoers entry limited to required commands
# echo "actions-runner ALL=(ALL) NOPASSWD: /sbin/zramctl, /sbin/swapon, /usr/bin/systemctl, /usr/sbin/sysctl" > /etc/sudoers.d/actions-runner

echo "Provision template created — follow inline comments to register runner via GitHub UI."
