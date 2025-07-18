# Telegram Family Bot (Russian)

A modular Telegram bot for your family with ChatGPT integration and room for future features. All interface text is in Russian.

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather and send `/newbot`
3. Follow the instructions to create your bot
4. Save the bot token you receive (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get OpenAI API Key

1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Create a new API key
4. Save the API key (starts with `sk-`)

### 3. Get WeatherAPI Key (Optional for Weather Feature)

1. Go to [WeatherAPI.com](https://www.weatherapi.com/)
2. Sign up for a free account (1 million calls/month free!)
3. Get your API key from the dashboard
4. Save the API key (the weather feature will work with a fallback if no key is provided)

### 4. Get User IDs (Optional but Recommended)

To restrict bot access to only your mom and wife:

1. Have them start a chat with your bot
2. Check the logs when they send `/start` to see their user IDs
3. Or use this temporary code to get their IDs

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your actual values:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token
   OPENAI_API_KEY=your_actual_openai_key
   WEATHERAPI_KEY=your_weatherapi_key
   ALLOWED_USER_IDS=123456789,987654321
   ```

### 7. Run the Bot

```bash
python telegram_chatgpt_bot.py
```

## Features

- ✅ **Russian Interface** - All messages and interface in Russian
- ✅ **Interactive Buttons** - Easy-to-use button interface (no complex commands!)
- ✅ **Secure Access** - Only specified users can use the bot
- ✅ **ChatGPT Integration** - Natural conversation with ChatGPT
- ✅ **WeatherAPI.com** - Real-time weather for Phuket, Thailand
- ✅ **Error Handling** - Graceful error handling and logging
- ✅ **Extensible** - Easy to add new features

## How It Works

### 🚀 **Super Simple Interface:**

1. **Start**: Type `/start` → See main menu with buttons
2. **ChatGPT**: Click "🤖 ChatGPT" button → Type questions naturally
3. **Weather**: Click "🌤️ Погода в Пхукете" button → Get instant weather
4. **Navigation**: Use "🔙 Назад в меню" to return to main menu

### 📱 **User Experience:**

Your family will see:
- **Main Menu**: Two clear buttons to choose from
- **ChatGPT Mode**: Just type questions like talking to a friend
- **Weather**: Instant weather info for Phuket with one click

## Usage Examples

Once running, your mom and wife can:

1. **Start the bot:**
   ```
   /start
   ```

2. **Use ChatGPT (click button, then type naturally):**
   ```
   Click: 🤖 ChatGPT
   Type: Расскажи анекдот
   Type: Как приготовить борщ?
   Type: Объясни что такое искусственный интеллект
   ```

3. **Get Weather (just click button):**
   ```
   Click: 🌤️ Погода в Пхукете
   ```

## Adding New Features

The bot is designed to be easily extensible. To add a new command:

1. Add the command text to the `MESSAGES` dictionary
2. Create a new async function for the command
3. Add the command handler in the `main()` function

Example structure for a new command:
```python
async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Your command logic here
    pass
```

## 🚀 Production Deployment

This bot is ready for production deployment! See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions using:

- **GitHub Actions** for automated CI/CD
- **Docker & DockerHub** for containerization  
- **DigitalOcean** for reliable hosting

### Quick Deployment Summary:
1. Create DigitalOcean droplet ($6/month)
2. Set up GitHub secrets (API keys, SSH keys)
3. Push to GitHub → Automatic deployment!

**Total cost**: ~$6-10/month for a reliable 24/7 bot that auto-updates when you push code changes.

## Security Notes

- The bot only responds to users listed in `ALLOWED_USER_IDS`
- Keep your `.env` file private and never commit it to version control
- Monitor your OpenAI API usage to avoid unexpected charges
- Use GitHub Secrets for production deployment (never hardcode API keys)