#!/usr/bin/env bash
# Set up the standalone station on a Raspberry Pi Zero 2 W (Raspberry Pi OS Lite, SSH on). Run from the laptop:
#   bash scripts/station.sh USER@opengonio.local
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
HOST=${1:?usage: bash scripts/station.sh USER@opengonio.local}
git archive --format=tar HEAD | ssh "$HOST" "rm -rf ~/opengonio && mkdir -p ~/opengonio && tar -x -C ~/opengonio"
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
