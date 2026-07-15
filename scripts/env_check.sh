#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"
pwd
uname -a
echo "${WSL_DISTRO_NAME:-}"
id -un
git --version
git config --global user.name
git config --global user.email
git config --global init.defaultBranch
command -v qcc
readlink -f "$(command -v qcc)"
test -x /home/kqdx/basilisk/src/qcc
[[ "$PWD" == /home/kqdx/basilisk_work/ring_fountain ]]
[[ "${WSL_DISTRO_NAME:-}" == Ubuntu ]]
[[ "$(id -un)" == kqdx ]]
[[ "$(readlink -f "$(command -v qcc)")" == /home/kqdx/basilisk/src/qcc ]]
command -v bwrap || true
echo "environment: PASS"

