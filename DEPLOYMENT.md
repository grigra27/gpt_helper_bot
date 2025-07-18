# 🚀 Deployment Guide: Telegram Bot to DigitalOcean

This guide will help you deploy your Telegram ChatGPT bot to DigitalOcean using GitHub Actions, Docker, and DockerHub.

## 📋 Prerequisites

- GitHub account
- DockerHub account
- DigitalOcean account
- Your bot tokens (Telegram, OpenAI, WeatherAPI)

## 🏗️ Step 1: Set Up DigitalOcean Droplet

### Create Droplet
1. Go to [DigitalOcean](https://www.digitalocean.com/)
2. Create a new Droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic plan, $6/month (1GB RAM, 1 vCPU)
   - **Region**: Choose closest to your users
   - **Authentication**: SSH Key (recommended) or Password

### Configure Server
1. SSH into your droplet:
   ```bash
   ssh root@your-droplet-ip
   ```

2. Run the setup script:
   ```bash
   curl -sSL https://raw.githubusercontent.com/yourusername/your-repo/main/deploy/setup-server.sh | bash
   ```

3. Reboot the server:
   ```bash
   sudo reboot
   ```

## 🐳 Step 2: Set Up DockerHub

1. Go to [DockerHub](https://hub.docker.com/)
2. Create account if you don't have one
3. Create a new repository:
   - **Name**: `telegram-chatgpt-bot`
   - **Visibility**: Private (recommended)
4. Generate Access Token:
   - Go to Account Settings → Security
   - Create new Access Token
   - Save the token securely

## 🔑 Step 3: Set Up SSH Key for Deployment

### Option A: Use Existing SSH Key (With or Without Passphrase)
If you already have an SSH key:
```bash
# Copy your existing public key to DigitalOcean droplet
ssh-copy-id -i ~/.ssh/id_rsa.pub root@your-droplet-ip

# Test SSH connection
ssh root@your-droplet-ip

# Get private key content for GitHub secrets
cat ~/.ssh/id_rsa
```

### Option B: Generate New SSH Key
```bash
# Generate SSH key (with or without passphrase - both work!)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com" -f ~/.ssh/digitalocean_deploy

# Copy public key to your DigitalOcean droplet
ssh-copy-id -i ~/.ssh/digitalocean_deploy.pub root@your-droplet-ip

# Test SSH connection
ssh -i ~/.ssh/digitalocean_deploy root@your-droplet-ip

# Get private key content for GitHub secrets
cat ~/.ssh/digitalocean_deploy
```

## 🔑 Step 4: Configure GitHub Secrets

In your GitHub repository, go to Settings → Secrets and variables → Actions, and add these secrets:

### DockerHub Secrets
- `DOCKERHUB_USERNAME`: Your DockerHub username
- `DOCKERHUB_TOKEN`: Your DockerHub access token

### DigitalOcean Secrets
- `DO_HOST`: Your droplet's IP address
- `DO_USERNAME`: `root` (or your created user)
- `DO_SSH_KEY`: Your private SSH key content
- `DO_SSH_PASSPHRASE`: Your SSH key passphrase (only if your key has one)

### Bot Configuration Secrets
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `OPENAI_API_KEY`: Your OpenAI API key
- `WEATHERAPI_KEY`: Your WeatherAPI key
- `ALLOWED_USER_IDS`: Comma-separated user IDs (e.g., `123456789,987654321`)

## 📁 Step 4: Prepare Your Repository

### Repository Structure
```
your-repo/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── deploy/
│   └── setup-server.sh
├── telegram_chatgpt_bot.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── .env.example
├── README.md
└── DEPLOYMENT.md
```

### Update .gitignore
Make sure your `.gitignore` includes:
```
.env
__pycache__/
*.pyc
logs/
```

## 🚀 Step 5: Deploy

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial deployment setup"
   git push origin main
   ```

2. **Monitor Deployment**:
   - Go to your GitHub repository
   - Click on "Actions" tab
   - Watch the deployment process

3. **Verify Deployment**:
   ```bash
   ssh root@your-droplet-ip
   docker ps  # Should show your running container
   docker logs telegram-chatgpt-bot  # Check bot logs
   ```

## 🔧 Step 6: Managing Your Bot

### Check Bot Status
```bash
ssh root@your-droplet-ip
docker ps
docker logs telegram-chatgpt-bot
```

### Restart Bot
```bash
ssh root@your-droplet-ip
docker restart telegram-chatgpt-bot
```

### Update Bot (Automatic)
Just push changes to your `main` branch - GitHub Actions will automatically:
1. Build new Docker image
2. Push to DockerHub
3. Deploy to DigitalOcean

### Manual Deployment
If you need to deploy manually:
```bash
ssh root@your-droplet-ip
docker pull yourusername/telegram-chatgpt-bot:latest
docker stop telegram-chatgpt-bot
docker rm telegram-chatgpt-bot
docker run -d --name telegram-chatgpt-bot --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN="your-token" \
  -e OPENAI_API_KEY="your-key" \
  -e WEATHERAPI_KEY="your-key" \
  -e ALLOWED_USER_IDS="123456789,987654321" \
  yourusername/telegram-chatgpt-bot:latest
```

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**:
   ```bash
   docker logs telegram-chatgpt-bot
   ```

2. **Container not starting**:
   ```bash
   docker ps -a
   docker logs telegram-chatgpt-bot
   ```

3. **GitHub Actions failing**:
   - Check secrets are correctly set
   - Verify SSH key has proper permissions
   - Check DockerHub credentials

4. **SSH Authentication Issues**:
   ```bash
   # Make sure you have the correct secrets set:
   # - DO_SSH_KEY: Your private key content
   # - DO_SSH_PASSPHRASE: Your key passphrase (if any)
   
   # Test SSH connection manually
   ssh root@your-droplet-ip
   
   # If using passphrase-protected key, make sure DO_SSH_PASSPHRASE secret is set
   ```

5. **SSH Connection Refused**:
   ```bash
   # Check if SSH service is running on server
   ssh root@your-droplet-ip "systemctl status ssh"
   
   # Check firewall settings
   ssh root@your-droplet-ip "ufw status"
   ```

### Useful Commands

```bash
# View all containers
docker ps -a

# View bot logs
docker logs -f telegram-chatgpt-bot

# Enter container shell
docker exec -it telegram-chatgpt-bot /bin/bash

# Check system resources
htop

# Check disk space
df -h
```

## 💰 Cost Estimation

### DigitalOcean
- **Basic Droplet**: $6/month (1GB RAM, 1 vCPU)
- **Bandwidth**: 1TB included

### APIs (Free Tiers)
- **Telegram Bot**: Free
- **OpenAI**: Pay per use (~$0.002 per 1K tokens)
- **WeatherAPI**: 1M calls/month free

**Total estimated cost**: ~$6-10/month

## 🔒 Security Best Practices

1. **Use SSH keys** instead of passwords
2. **Keep secrets in GitHub Secrets**, never in code
3. **Regularly update** your droplet and Docker images
4. **Monitor logs** for suspicious activity
5. **Use firewall** (UFW is configured in setup script)

## 📈 Monitoring

### Set Up Monitoring (Optional)
1. **DigitalOcean Monitoring**: Enable in droplet settings
2. **Uptime monitoring**: Use services like UptimeRobot
3. **Log monitoring**: Set up log alerts

Your bot is now deployed and will automatically update when you push changes to GitHub! 🎉