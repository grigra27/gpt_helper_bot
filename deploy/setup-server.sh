#!/bin/bash

# DigitalOcean Server Setup Script for Telegram Bot
# Run this script on your DigitalOcean droplet

set -e

echo "🚀 Setting up DigitalOcean server for Telegram Bot deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -aG docker $USER

# Install additional tools
echo "🛠️ Installing additional tools..."
sudo apt install -y htop nano git ufw

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw --force enable

# Create directories
echo "📁 Creating application directories..."
mkdir -p ~/telegram-bot/logs

# Set up log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/docker-containers > /dev/null <<EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF

# Create systemd service for automatic container management
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/telegram-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram ChatGPT Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/docker start telegram-chatgpt-bot
ExecStop=/usr/bin/docker stop telegram-chatgpt-bot
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable telegram-bot.service

echo "✅ Server setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Reboot the server: sudo reboot"
echo "2. Set up your GitHub repository secrets"
echo "3. Push your code to trigger deployment"
echo ""
echo "🔑 Don't forget to add your SSH public key to GitHub secrets!"
echo "Generate one with: ssh-keygen -t rsa -b 4096 -C 'your-email@example.com'"