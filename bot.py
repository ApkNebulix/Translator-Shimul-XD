import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# --- PRE-CONFIG ---
TOKEN = "8755517901:AAHTZX9MifygQsJ9NaFg_3NABKhvwBbEYw8"
ADMIN_ID = 8381570120
VERSION = "2.0 Pro"

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Supported Languages (Commonly used, but system supports 100+)
LANG_MAP = {
    "bn": "Bengali 🇧🇩",
    "en": "English 🇺🇸",
    "ar": "Arabic 🇸🇦",
    "hi": "Hindi 🇮🇳",
    "es": "Spanish 🇪🇸",
    "fr": "French 🇫🇷",
    "de": "German 🇩🇪",
    "it": "Italian 🇮🇹",
    "ja": "Japanese 🇯🇵",
    "ru": "Russian 🇷🇺"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if 'target' not in context.user_data:
        context.user_data['target'] = 'bn'

    welcome_text = (
        f"👑 *Premium Translator v{VERSION}*\n\n"
        f"Welcome, *{user.first_name}*!\n"
        f"I am a professional AI-powered translator developed by *Shimul XD*.\n\n"
        f"✨ *Current Settings:*\n"
        f"🔹 Target Language: `{LANG_MAP.get(context.user_data['target'], 'Unknown')}`\n"
        f"🔹 Engine: `AI Deep-Translate`\n"
        f"🔹 Auto-Detection: `Enabled` ✅\n\n"
        f"Simply send me any text, and I will translate it for you instantly!"
    )

    keyboard = [
        [InlineKeyboardButton("Change Language 🌐", callback_data='change_lang')],
        [InlineKeyboardButton("Support 👨‍💻", url="https://t.me/ShimulXD")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def change_lang_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    buttons = []
    keys = list(LANG_MAP.keys())
    for i in range(0, len(keys), 2):
        row = [
            InlineKeyboardButton(LANG_MAP[keys[i]], callback_data=f"set_{keys[i]}"),
            InlineKeyboardButton(LANG_MAP[keys[i+1]], callback_data=f"set_{keys[i+1]}") if i+1 < len(keys) else None
        ]
        buttons.append([b for b in row if b])

    await query.edit_message_text(
        "✨ *Select Target Language*\nChoose the language you want to translate to:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode='Markdown'
    )

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang_code = query.data.replace('set_', '')
    context.user_data['target'] = lang_code
    await query.answer(f"Language set to {LANG_MAP[lang_code]}")
    await start(update.callback_query, context) # Refresh menu

async def translate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text or text.startswith('/'): return

    target = context.user_data.get('target', 'bn')
    proc_msg = await update.message.reply_text("🔄 *Processing with AI...*", parse_mode='Markdown')

    try:
        # Professional Translation Engine
        translator = GoogleTranslator(source='auto', target=target)
        translated = translator.translate(text)

        # Response Construction
        response = (
            f"✅ *Translation Completed*\n\n"
            f"📥 *Original:* `{text}`\n\n"
            f"📤 *Result ({target.upper()}):*\n`{translated}`\n\n"
            f"👤 *Translator:* @ShimulXD"
        )
        
        # Audio Feature (TTS) for Premium Feel
        keyboard = [[InlineKeyboardButton("Listen 🔊", callback_data=f"tts_{target}")]]
        context.user_data['last_trans'] = translated

        await proc_msg.edit_text(response, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    except Exception as e:
        await proc_msg.edit_text(f"❌ *Error:* Failed to translate. Please try again later.\n`{str(e)}`", parse_mode='Markdown')

async def tts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Generating Audio...")
    
    text = context.user_data.get('last_trans')
    lang = query.data.split('_')[1]

    if text:
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save("trans.mp3")
            await query.message.reply_audio(audio=open("trans.mp3", 'rb'), caption="🔊 Pronunciation")
            os.remove("trans.mp3")
        except:
            await query.answer("Audio not supported for this language.", show_alert=True)

# Admin Commands
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"📊 *Admin Statistics*\n\nStatus: Online 🟢\nVersion: {VERSION}\nHost: GitHub Actions", parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CallbackQueryHandler(change_lang_menu, pattern='change_lang'))
    app.add_handler(CallbackQueryHandler(set_lang, pattern='^set_'))
    app.add_handler(CallbackQueryHandler(tts_handler, pattern='^tts_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_handler))

    print("🚀 Premium Bot is Running...")
    app.run_polling()

if __name__ == '__main__':
    main()
