import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.genai as genai

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Проверяем наличие токенов
if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    logger.error("❌ Не заданы TELEGRAM_TOKEN или GEMINI_API_KEY!")
    exit(1)

# Инициализация Gemini
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini подключен")
except Exception as e:
    logger.error(f"❌ Ошибка Gemini: {e}")
    exit(1)

# =============== ОБРАБОТЧИКИ ===============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🏗️ *EXPERT READER BOT*\n\n"
        "Я бот для анализа строительных экспертиз.\n\n"
        "Отправьте мне текст или документ для анализа.\n\n"
        "🤖 *Команды:*\n"
        "/start - начать работу\n"
        "/help - помощь\n"
        "/analyze текст - анализ текста",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "📋 *ПОМОЩЬ*\n\n"
        "Я анализирую строительные документы с помощью AI.\n\n"
        "📤 *Что можно отправить:*\n"
        "• Текст заключения\n"
        "• Вопрос по экспертизе\n"
        "• Описание проблемы\n\n"
        "⚙️ *Технологии:*\n"
        "• Telegram Bot API\n"
        "• Google Gemini AI\n"
        "• Railway хостинг",
        parse_mode='Markdown'
    )

async def analyze_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Анализ текста через Gemini"""
    text = ' '.join(context.args)
    
    if not text:
        await update.message.reply_text("❌ Укажите текст для анализа: /analyze ваш текст")
        return
    
    try:
        # Показываем, что бот "печатает"
        await update.message.reply_chat_action(action="typing")
        
        # Запрос к Gemini
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[f"Ты строительный эксперт. Проанализируй: {text}"],
            config={"temperature": 0.1, "max_output_tokens": 1000}
        )
        
        await update.message.reply_text(
            f"📊 *АНАЛИЗ ТЕКСТА*\n\n{response.text}",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка анализа: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    text = update.message.text
    
    try:
        await update.message.reply_chat_action(action="typing")
        
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[f"Ответь как строительный эксперт на: {text}"],
            config={"temperature": 0.1, "max_output_tokens": 500}
        )
        
        await update.message.reply_text(
            f"🤖 *ОТВЕТ ЭКСПЕРТА*\n\n{response.text}",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")

def main():
    """Запуск бота"""
    print("🚀 ЗАПУСК БОТА НА RAILWAY...")
    
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyze", analyze_text))
    
    # Обработчик обычных сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    app.add_error_handler(error_handler)
    
    print("✅ БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ!")
    print(f"🤖 Телеграм бот: https://t.me/ExpertReader_Bot")
    
    # Запускаем polling
    app.run_polling(
        poll_interval=1.0,
        timeout=10,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
