import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from deep_translator import GoogleTranslator

# --- CONFIGURATION ---
TOKEN = "8755517901:AAHTZX9MifygQsJ9NaFg_3NABKhvwBbEYw8"
ADMIN_ID = 8381570120

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    # Default Target Language: Bengali
    if 'target_lang' not in context.user_data:
        context.user_data['target_lang'] = 'bn'

    text = (
        f"👋 **স্বাগতম বন্ধু {user_name}!**\n\n"
        f"আমি একটি **Premium AI Translator Bot**।\n"
        f"যেকোনো টেক্সট আমাকে পাঠাও, আমি অটো-ডিটেক্ট করে সেটি অনুবাদ করে দেব।\n\n"
        f"⚙️ **বর্তমান টার্গেট ভাষা:** `{context.user_data['target_lang'].upper()}`\n\n"
        f"নিচের বাটন থেকে ভাষা পরিবর্তন করতে পারো:"
    )
    
    keyboard = [
        [InlineKeyboardButton("Bengali 🇧🇩", callback_data='set_bn'),
         InlineKeyboardButton("English 🇺🇸", callback_data='set_en')],
        [InlineKeyboardButton("Arabic 🇸🇦", callback_data='set_ar'),
         InlineKeyboardButton("Hindi 🇮🇳", callback_data='set_hi')],
        [InlineKeyboardButton("Spanish 🇪🇸", callback_data='set_es'),
         InlineKeyboardButton("French 🇫🇷", callback_data='set_fr')]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace('set_', '')
    context.user_data['target_lang'] = lang_code
    
    await query.edit_message_text(
        f"✅ **টার্গেট ভাষা সফলভাবে পরিবর্তন করা হয়েছে!**\n"
        f"এখন থেকে সব অনুবাদ **{lang_code.upper()}** ভাষায় হবে।",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back 🔙", callback_data='back_start')]]),
        parse_mode='Markdown'
    )

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # রি-কল স্টার্ট ফাংশন logic
    await start(update, context)

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text.startswith('/'): return

    target = context.user_data.get('target_lang', 'bn')
    
    # প্রসেসিং মেসেজ
    processing_msg = await update.message.reply_text("⏳ অনুবাদ হচ্ছে বন্ধু, একটু অপেক্ষা করো...")

    try:
        # Deep Translator Logic (Auto Detection is Built-in)
        translated = GoogleTranslator(source='auto', target=target).translate(user_text)
        
        response = (
            f"🌐 **Translation Successful**\n\n"
            f"📝 **Original:** `{user_text}`\n\n"
            f"🔄 **Translated ({target.upper()}):**\n`{translated}`\n\n"
            f"👤 **Translator:** @ShimulXD"
        )
        await processing_msg.edit_text(response, parse_mode='Markdown')
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await processing_msg.edit_text("❌ দুঃখিত বন্ধু! অনুবাদ করার সময় একটি টেকনিক্যাল সমস্যা হয়েছে।")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("📊 বটটি বর্তমানে সচল আছে এবং গিটহাব অ্যাকশনে রান করছে।")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler, pattern='^set_'))
    app.add_handler(CallbackQueryHandler(back_to_start, pattern='back_start'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))

    print("🚀 Bot Started Successfully!")
    app.run_polling()

if __name__ == '__main__':
    main()
