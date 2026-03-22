import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from googletrans import Translator

# --- CONFIGURATION ---
TOKEN = "8755517901:AAHTZX9MifygQsJ9NaFg_3NABKhvwBbEYw8"
ADMIN_ID = 8381570120
translator = Translator()

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ডিফল্ট ল্যাংগুয়েজ সেট করা যদি না থাকে
    if 'lang' not in context.user_data:
        context.user_data['lang'] = 'bn' # ডিফল্ট বাংলা

    welcome_msg = (
        f"🌟 **Premium Translator Bot** 🌟\n\n"
        f"হ্যালো {update.effective_user.first_name}!\n"
        f"আমি শিমুল এক্সডি-র তৈরি একটি শক্তিশালী অনুবাদক।\n\n"
        f"🔹 **বর্তমান টার্গেট ভাষা:** {context.user_data['lang'].upper()}\n"
        f"🔹 **ফিচার:** অটো ডিটেকশন ও ১০০+ ভাষা সাপোর্ট।\n\n"
        f"অনুবাদ করতে চাইলে যেকোনো টেক্সট এখানে পাঠাও।"
    )
    
    keyboard = [
        [InlineKeyboardButton("Bengali 🇧🇩", callback_data='set_bn'),
         InlineKeyboardButton("English 🇺🇸", callback_data='set_en')],
        [InlineKeyboardButton("Arabic 🇸🇦", callback_data='set_ar'),
         InlineKeyboardButton("Hindi 🇮🇳", callback_data='set_hi')],
        [InlineKeyboardButton("Change Language 🌐", callback_data='show_all')]
    ]
    await update.message.reply_text(welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('set_'):
        lang = query.data.split('_')[1]
        context.user_data['lang'] = lang
        await query.edit_message_text(f"✅ টার্গেট ভাষা সেট করা হয়েছে: **{lang.upper()}**\nএখন যেকোনো টেক্সট পাঠান, আমি অনুবাদ করে দেব।", parse_mode='Markdown')
    
    elif query.data == 'show_all':
        await query.edit_message_text("অন্যান্য ভাষার জন্য লিখুন: `/set ভাষা_কোড` (যেমন: `/set fr` ফ্রেঞ্চের জন্য)")

async def translate_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text or text.startswith('/'): return

    # টার্গেট ভাষা নির্ধারণ
    target = context.user_data.get('lang', 'bn')
    
    msg = await update.message.reply_text("🔄 অনুবাদ হচ্ছে, দয়া করে অপেক্ষা করুন...")

    try:
        # Translation Process
        result = translator.translate(text, dest=target)
        
        response = (
            f"✅ **অনুবাদ সম্পন্ন হয়েছে!**\n\n"
            f"📥 **থেকে:** {result.src.upper()}\n"
            f"📤 **টেক্সট:** `{result.text}`\n\n"
            f"👤 *Translator - Shimul XD*"
        )
        await msg.edit_text(response, parse_mode='Markdown')
    except Exception as e:
        await msg.edit_text(f"❌ এরর: অনুবাদ করা সম্ভব হয়নি।\nসম্ভাব্য কারণ: {str(e)}")

async def set_lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        lang = context.args[0].lower()
        context.user_data['lang'] = lang
        await update.message.reply_text(f"✅ ভাষা পরিবর্তন করে **{lang.upper()}** করা হয়েছে।")
    else:
        await update.message.reply_text("সঠিক নিয়ম: `/set en` বা `/set bn`।")

def main():
    # Application build
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set", set_lang_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_msg))

    print("✅ Bot is Online and ready to translate!")
    app.run_polling()

if __name__ == '__main__':
    main()
