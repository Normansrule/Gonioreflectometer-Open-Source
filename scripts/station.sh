#!/usr/bin/env bash
# Set up the standalone station on a Raspberry Pi Zero 2 W (Raspberry Pi OS Lite, SSH on). Run from the laptop:
#   bash scripts/station.sh USER@opengonio.local
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
HOST=${1:?usage: bash scripts/station.sh USER@opengonio.local}
# Update keeps the station's own machine.yaml and calibration.yaml: the new code goes to ~/opengonio.new, the two files
# are carried over from the old install (the repo's machine.yaml is left beside it as machine.yaml.repo to compare),
# the old install is kept as ~/opengonio.prev. Nothing measured is lost by re-running this script.
git archive --format=tar HEAD | ssh "$HOST" 'set -e; rm -rf ~/opengonio.new; mkdir -p ~/opengonio.new; tar -x -C ~/opengonio.new
for f in machine.yaml calibration.yaml; do
  if [ -f ~/opengonio/software/config/$f ]; then
    [ "$f" = machine.yaml ] && cp ~/opengonio.new/software/config/$f ~/opengonio.new/software/config/$f.repo
    cp -p ~/opengonio/software/config/$f ~/opengonio.new/software/config/$f
    echo "kept the station $f"
    if [ "$f" = machine.yaml ] && ! cmp -s ~/opengonio.new/software/config/$f ~/opengonio.new/software/config/$f.repo; then
      echo "NOTE the repo machine.yaml changed: compare with diff ~/opengonio/software/config/machine.yaml{,.repo}"
    fi
  fi
done
if [ -d ~/opengonio ]; then rm -rf ~/opengonio.prev; mv ~/opengonio ~/opengonio.prev; fi
mv ~/opengonio.new ~/opengonio'

ssh "$HOST" 'bash -s' <<'REMOTE'
set -e
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-opencv python3-numpy python3-yaml python3-serial v4l-utils rsync
sudo raspi-config nonint do_serial_hw 0      # UART on
sudo raspi-config nonint do_serial_cons 1    # no login console on it
cd ~/opengonio
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -q --no-deps -e ./software
printf '%s\n' \
  '[Unit]' 'Description=OpenGonio standalone station' 'After=network-online.target' \
  '[Service]' "User=$USER" "WorkingDirectory=$HOME/opengonio" "ExecStart=$HOME/opengonio/.venv/bin/opengonio station" \
  'Restart=on-failure' 'RestartSec=5' \
  '[Install]' 'WantedBy=multi-user.target' | sudo tee /etc/systemd/system/opengonio-station.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable opengonio-station
echo "Installed. Reboot once for the UART: sudo reboot"
REMOTE
echo "Logs: ssh $HOST journalctl -u opengonio-station -f"
