#!/bin/bash

echo "=== BOMI Bot Server Status Check ==="
echo ""

echo "1. Service Status:"
systemctl status bomi-bot --no-pager | head -15
echo ""

echo "2. Recent Logs (last 20 lines):"
journalctl -u bomi-bot -n 20 --no-pager
echo ""

echo "3. Bot Process:"
ps aux | grep "python.*start_bot.py" | grep -v grep
echo ""

echo "4. Git Status:"
cd /root/bomi-bot
git log -1 --oneline
echo ""

echo "5. Python Dependencies:"
pip3 list | grep -E "telegram|openai|requests"
echo ""

echo "=== Quick Commands ==="
echo "Restart: systemctl restart bomi-bot"
echo "Logs: journalctl -u bomi-bot -f"
echo "Stop: systemctl stop bomi-bot"
