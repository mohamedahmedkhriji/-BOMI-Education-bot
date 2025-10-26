#!/bin/bash

# BOMI Bot Service Setup Script

SERVICE_NAME="bomi-bot"
BOT_DIR="/root/-BOMI-Education-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Creating systemd service for BOMI Bot..."

# Create service file
cat > $SERVICE_FILE << EOF
[Unit]
Description=BOMI DTM Education Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${BOT_DIR}
ExecStart=python3 start_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable ${SERVICE_NAME}

# Start service
systemctl start ${SERVICE_NAME}

echo "Service created and started!"
echo "Commands:"
echo "  Status:  systemctl status ${SERVICE_NAME}"
echo "  Stop:    systemctl stop ${SERVICE_NAME}"
echo "  Start:   systemctl start ${SERVICE_NAME}"
echo "  Restart: systemctl restart ${SERVICE_NAME}"
echo "  Logs:    journalctl -u ${SERVICE_NAME} -f"
