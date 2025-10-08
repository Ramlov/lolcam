#!/usr/bin/env bash
# Completely reset Python on Linux (Ubuntu/Debian)

set -e

echo "=== 🚨 WARNING: This will remove ALL Python installations, packages, and configs (except system-critical python3) ==="
read -p "Continue? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" ]]; then
  echo "Aborted."
  exit 1
fi

echo "=== 🔍 Checking current Python installations ==="
which -a python python3 || true

echo "=== 🧹 Removing pip packages and caches ==="
pip freeze 2>/dev/null | xargs pip uninstall -y 2>/dev/null || true
pip3 freeze 2>/dev/null | xargs pip3 uninstall -y 2>/dev/null || true
rm -rf ~/.local/lib/python*
rm -rf ~/.cache/pip
rm -rf ~/.config/pip

echo "=== 🗑️ Removing user Python installs ==="
sudo rm -rf /usr/local/bin/python* /usr/local/lib/python* /usr/local/include/python* 2>/dev/null || true
sudo rm -rf /opt/python* 2>/dev/null || true

echo "=== 🧩 Removing pyenv and Anaconda if present ==="
rm -rf ~/.pyenv ~/.conda ~/.continuum ~/anaconda3 ~/miniconda3

echo "=== 🧼 Cleaning PATH entries in shell configs ==="
for file in ~/.bashrc ~/.zshrc; do
  if [[ -f "$file" ]]; then
    sed -i '/python/d' "$file"
    sed -i '/pip/d' "$file"
    sed -i '/conda/d' "$file"
    sed -i '/pyenv/d' "$file"
  fi
done

echo "=== 🧰 Removing APT-installed Python (not system-critical one) ==="
sudo apt purge -y python3 python3-pip || true
sudo apt autoremove -y

echo "=== 🔄 Reinstalling fresh Python and pip ==="
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv

echo "=== ✅ Done! Installed Python version: ==="
python3 --version
pip3 --version

echo "=== 🧽 Cleanup complete! You now have a fresh Python install. ==="
