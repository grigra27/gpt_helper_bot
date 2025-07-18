import os
import logging
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Get allowed user IDs from environment
ALLOWED_USER_IDS = set()
if os.getenv('ALLOWED_USER_IDS'):
    ALLOWED_USER_IDS = set(map(int, os.getenv('ALLOWED_USER_IDS').split(',')))

# Conversation states
MAIN_MENU, CHATGPT_MODE = range(2)

# Button texts
CHATGPT_BUTTON = "🤖 ChatGPT"
WEATHER_BUTTON = "🌤️ Погода в Пхукете"
BACK_BUTTON = "🔙 Назад в меню"

# Russian text messages
MESSAGES = {
    'not_authorized': 'Извините, у вас нет доступа к этому боту.',
    'welcome': '''Привет! 👋 Я ваш персональный помощник.

Выберите, что вы хотите сделать:''',
    
    'chatgpt_mode': '''🤖 Режим ChatGPT активирован!

Теперь просто напишите мне любой вопрос, и я отвечу с помощью ChatGPT.

Примеры:
• Расскажи анекдот
• Как приготовить борщ?
• Объясни что такое искусственный интеллект
• Помоги написать письмо

Для возврата в главное меню нажмите кнопку "Назад в меню".''',
    
    'chatgpt_error': 'Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз через минуту.',
    'weather_error': 'Извините, не удалось получить данные о погоде. Попробуйте позже.',
    'back_to_menu': 'Возвращаемся в главное меню. Выберите действие:'
}

def is_user_allowed(user_id: int) -> bool:
    """Check if user is allowed to use the bot"""
    return len(ALLOWED_USER_IDS) == 0 or user_id in ALLOWED_USER_IDS

def get_main_keyboard():
    """Create main menu keyboard"""
    keyboard = [
        [KeyboardButton(CHATGPT_BUTTON)],
        [KeyboardButton(WEATHER_BUTTON)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_chatgpt_keyboard():
    """Create ChatGPT mode keyboard"""
    keyboard = [
        [KeyboardButton(BACK_BUTTON)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - show main menu"""
    user_id = update.effective_user.id
    
    if not is_user_allowed(user_id):
        await update.message.reply_text(MESSAGES['not_authorized'])
        return ConversationHandler.END
    
    await update.message.reply_text(
        MESSAGES['welcome'],
        reply_markup=get_main_keyboard()
    )
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu button presses"""
    user_id = update.effective_user.id
    
    if not is_user_allowed(user_id):
        await update.message.reply_text(MESSAGES['not_authorized'])
        return ConversationHandler.END
    
    text = update.message.text
    
    if text == CHATGPT_BUTTON:
        await update.message.reply_text(
            MESSAGES['chatgpt_mode'],
            reply_markup=get_chatgpt_keyboard()
        )
        return CHATGPT_MODE
    
    elif text == WEATHER_BUTTON:
        await weather_command(update, context)
        return MAIN_MENU
    
    else:
        await update.message.reply_text(
            MESSAGES['welcome'],
            reply_markup=get_main_keyboard()
        )
        return MAIN_MENU

async def handle_chatgpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle messages in ChatGPT mode"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    if not is_user_allowed(user_id):
        await update.message.reply_text(MESSAGES['not_authorized'])
        return ConversationHandler.END
    
    text = update.message.text
    
    # Check if user wants to go back to main menu
    if text == BACK_BUTTON:
        await update.message.reply_text(
            MESSAGES['back_to_menu'],
            reply_markup=get_main_keyboard()
        )
        return MAIN_MENU
    
    # Process ChatGPT request
    logger.info(f"ChatGPT request from {user_name} (ID: {user_id}): {text}")
    
    try:
        # Send "typing" action to show bot is working
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Send message to ChatGPT
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond in Russian in a friendly and conversational manner."},
                {"role": "user", "content": text}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Extract the response text
        chatgpt_response = response.choices[0].message.content.strip()
        
        # Send response back to user
        await update.message.reply_text(chatgpt_response)
        
        # Log the response
        logger.info(f"ChatGPT response sent to {user_name}: {chatgpt_response[:100]}...")
        
    except Exception as e:
        logger.error(f"Error processing ChatGPT request: {str(e)}")
        await update.message.reply_text(MESSAGES['chatgpt_error'])
    
    return CHATGPT_MODE

def get_weather_emoji(condition_text: str) -> str:
    """Get weather emoji based on weather condition from WeatherAPI"""
    condition_lower = condition_text.lower()
    
    if 'sunny' in condition_lower or 'clear' in condition_lower:
        return '☀️'
    elif 'partly cloudy' in condition_lower:
        return '⛅'
    elif 'cloudy' in condition_lower or 'overcast' in condition_lower:
        return '☁️'
    elif 'rain' in condition_lower or 'drizzle' in condition_lower:
        return '🌧️'
    elif 'thunder' in condition_lower or 'storm' in condition_lower:
        return '⛈️'
    elif 'snow' in condition_lower:
        return '❄️'
    elif 'mist' in condition_lower or 'fog' in condition_lower:
        return '🌫️'
    else:
        return '🌤️'

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get current weather for Phuket, Thailand using WeatherAPI.com"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    if not is_user_allowed(user_id):
        await update.message.reply_text(MESSAGES['not_authorized'])
        return
    
    logger.info(f"Weather request from {user_name} (ID: {user_id})")
    
    try:
        # Send "typing" action to show bot is working
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # WeatherAPI.com API call for Phuket, Thailand
        api_key = os.getenv('WEATHERAPI_KEY')
        if not api_key:
            # If no API key, use fallback information
            weather_response = "🌴 Пхукет, Таиланд\n\n"
            weather_response += "⚠️ Для получения актуальной погоды нужен API ключ WeatherAPI.com\n\n"
            weather_response += "Обычная погода в Пхукете:\n"
            weather_response += "🌡️ Температура: 28-32°C\n"
            weather_response += "💧 Влажность: 70-80%\n"
            weather_response += "🌴 Тропический климат круглый год"
            await update.message.reply_text(weather_response)
            return
        
        # WeatherAPI.com endpoint for Phuket
        location = "Phuket,Thailand"
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&lang=ru"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        weather_data = response.json()
        
        # Extract weather information from WeatherAPI response
        location_info = weather_data['location']
        current = weather_data['current']
        
        city = location_info['name']
        country = location_info['country']
        temp = round(current['temp_c'])
        feels_like = round(current['feelslike_c'])
        humidity = current['humidity']
        condition = current['condition']['text']
        wind_speed = round(current['wind_kph'] / 3.6, 1)  # Convert km/h to m/s
        uv_index = current['uv']
        
        # Get weather emoji
        emoji = get_weather_emoji(condition)
        
        # Format weather message in Russian
        weather_response = f"🌴 {city}, {country}\n\n"
        weather_response += f"{emoji} {condition}\n"
        weather_response += f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
        weather_response += f"💧 Влажность: {humidity}%\n"
        weather_response += f"💨 Ветер: {wind_speed} м/с\n"
        weather_response += f"☀️ УФ-индекс: {uv_index}\n\n"
        weather_response += f"🕐 Обновлено: {datetime.now().strftime('%H:%M')}"
        
        await update.message.reply_text(weather_response)
        logger.info(f"Weather data sent to {user_name}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API error: {str(e)}")
        await update.message.reply_text(MESSAGES['weather_error'])
    except KeyError as e:
        logger.error(f"Weather data parsing error: {str(e)}")
        await update.message.reply_text(MESSAGES['weather_error'])
    except Exception as e:
        logger.error(f"Error getting weather: {str(e)}")
        await update.message.reply_text(MESSAGES['weather_error'])

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation and return to main menu"""
    await update.message.reply_text(
        MESSAGES['back_to_menu'],
        reply_markup=get_main_keyboard()
    )
    return MAIN_MENU

def main() -> None:
    """Start the bot."""
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not found in environment variables")
        return
    
    # Create the Application
    application = Application.builder().token(bot_token).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
            ],
            CHATGPT_MODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chatgpt_message)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    # Add conversation handler
    application.add_handler(conv_handler)
    
    # Log startup
    logger.info("Bot is starting...")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()