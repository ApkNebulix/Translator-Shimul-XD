import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQuery_Handler, filters, ContextTypes
from googletrans import Translator, LANGUAGES

# --- CONFIGURATION ---
TOKEN = "8755517901:AAHTZX9MifygQsJ9NaFg_3NABKhvwBbEYw8"
ADMIN_ID = 8381570120
translator = Translator()

# ইন-মেমোরি ইউজার সেটিংস (ডিফল্ট অনুবাদ ভাষা: ইংরেজি)
user_settings = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_settings:
        user_settings[user_id] = 'en' # Default language
    
    welcome_text = (
        f"👋 সালাম বন্ধু {update.effective_user.first_name}!\n\n"
        "আমি একটি শক্তিশালী অনুবাদক বট।\n"
        "✅ যেকোনো ভাষায় টেক্সট পাঠাও, আমি সেটি অনুবাদ করে দেব।\n"
        "✅ অটো ল্যাংগুয়েজ ডিটেকশন সিস্টেম সচল।\n\n"
        "নিচের বাটন থেকে তোমার পছন্দের টার্গেট ভাষা সেট করো।"
    )
    
    keyboard = [
        [InlineKeyboardButton("Bengali 🇧🇩", callback_data='set_bn'),
         InlineKeyboardButton("English 🇺🇸", callback_data='set_en')],
        [InlineKeyboardButton("Arabic 🇸🇦", callback_data='set_ar'),
         InlineKeyboardButton("Hindi 🇮🇳", callback_data='set_hi')],
        [InlineKeyboardButton("More Languages 🌐", callback_data='more_lang')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace('set_', '')
    if lang_code == 'more_lang':
        await query.edit_message_text("সব ভাষা সাপোর্ট করে! শুধু লিখুন: `/set ভাষা_কোড` (যেমন: `/set fr` ফ্রেঞ্চের জন্য)")
        return

    user_settings[query.from_user.id] = lang_code
    await query.edit_message_text(f"✅ টার্গেট ভাষা সেট করা হয়েছে: *{LANGUAGES.get(lang_code).upper()}*", parse_mode='Markdown')

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if text.startswith('/'): return

    target_lang = user_settings.get(user_id, 'en')
    
    try:
        # Detect and Translate
        detection = translator.detect(text)
        src_lang = detection.lang
        translation = translator.translate(text, dest=target_lang)
        
        response = (
            f"🌐 *Translation Result*\n\n"
            f"📝 *Original ({src_lang}):* {text}\n"
            f"🔄 *Translated ({target_lang}):* {translation.text}\n\n"
            f"💡 _Detected Language: {LANGUAGES.get(src_lang, src_lang).capitalize()}_"
        )
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ দুঃখিত বন্ধু, অনুবাদ করতে সমস্যা হয়েছে। আবার চেষ্টা করো।\nError: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"📊 বটের বর্তমান ব্যবহারকারী সংখ্যা (সেশন): {len(user_settings)}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(set_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
