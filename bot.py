#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neon Prediction Telegram Bot
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from supabase import create_client, Client

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@NeonPredictionEG")
ADMIN_ID = os.getenv("ADMIN_ID")

GAME_URL = "https://neon-game-seven.vercel.app?ref=2A9MAC"
REFERRAL_CODE = "2A9MAC"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase connected")
    except Exception as e:
        logger.error(f"Supabase error: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "صديقي"
    
    text = f"""🎮 أهلاً بيك يا {name} في Neon Prediction!

🎯 توقع – العب – اكسب
💰 سحب حقيقي من 100ج
🎁 بونص ترحيبي 10 نقاط
🎡 عجلة حظ يومياً (جاكبوت 25ج 💎)
⚡ برايم = مضاعف ×2

اضغط على الأزرار تحت:"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 ابدأ اللعب", url=GAME_URL)],
        [InlineKeyboardButton("📊 إحصائيات", callback_data="stats"),
         InlineKeyboardButton("🏆 أعلى اللاعبين", callback_data="top")],
        [InlineKeyboardButton("🎁 كود البونص", callback_data="bonus"),
         InlineKeyboardButton("👥 كود الإحالة", callback_data="myref")],
        [InlineKeyboardButton("📢 القناة", url="https://t.me/NeonPredictionEG")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not supabase:
        await update.message.reply_text("⚠️ قاعدة البيانات مش متصلة")
        return
    
    try:
        users_res = supabase.table('users').select('id').execute()
        total_users = len(users_res.data) if users_res.data else 0
        
        text = f"""📊 إحصائيات Neon Prediction

👥 إجمالي اللاعبين: {total_users}
🎮 الموقع: {GAME_URL}
🎁 بونص ترحيبي: 10 نقاط
💰 الحد الأدنى للسحب: 100ج"""
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"stats error: {e}")
        await update.message.reply_text("⚠️ حصل خطأ، جرب تاني")


async def top_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not supabase:
        await update.message.reply_text("⚠️ قاعدة البيانات مش متصلة")
        return
    
    try:
        res = supabase.table('users').select('username, purchased, earned, wins').order('earned', desc=True).limit(10).execute()
        
        if not res.data:
            await update.message.reply_text("لا يوجد لاعبين لسه")
            return
        
        text = "🏆 أعلى 10 لاعبين:\n\n"
        medals = ['🥇', '🥈', '🥉']
        for i, u in enumerate(res.data):
            medal = medals[i] if i < 3 else f"{i+1}."
            name = u.get('username', 'مجهول')
            points = (u.get('purchased', 0) or 0) + (u.get('earned', 0) or 0)
            text += f"{medal} {name} — {points} نقطة\n"
        
        await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"top error: {e}")
        await update.message.reply_text("⚠️ حصل خطأ، جرب تاني")


async def my_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""👥 نظام الإحالة

💰 كل صديق يسجل بكودك = 5 جنيه مجاناً
🎯 10 أصحاب = 50 جنيه

كودك الخاص:
{REFERRAL_CODE}

اللينك:
{GAME_URL}

📌 شارك اللينك مع أصحابك وابدأ تكسب!"""
    keyboard = [[InlineKeyboardButton("📤 شارك اللينك", url=f"https://t.me/share/url?url={GAME_URL}&text=العب معايا Neon Prediction!")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    code = f"NEON{datetime.now().strftime('%d%m')}"
    
    text = f"""🎁 كود بونص النهاردة

📅 التاريخ: {today}
🎟️ الكود: {code}

📌 طريقة الاستخدام:
1. سجّل في الموقع
2. روح تبويب "الأكواد"
3. اكتب الكود
4. هتاخد 10 نقاط فوراً

⏰ صالح لمدة 24 ساعة

🔗 {GAME_URL}"""
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🆘 المساعدة والدعم

الأوامر المتاحة:
/start — القائمة الرئيسية
/stats — إحصائيات الموقع
/top — أعلى 10 لاعبين
/bonus — كود بونص اليوم
/myref — كود الإحالة
/help — المساعدة

للدعم: تواصل مع الأدمن"""
    await update.message.reply_text(text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "stats":
        try:
            users_res = supabase.table('users').select('id').execute()
            total_users = len(users_res.data) if users_res.data else 0
            text = f"📊 إحصائيات Neon Prediction\n\n👥 إجمالي اللاعبين: {total_users}\n🎮 {GAME_URL}\n🎁 بونص ترحيبي: 10 نقاط\n💰 الحد الأدنى للسحب: 100ج"
            await query.message.reply_text(text)
        except Exception as e:
            logger.error(f"stats button error: {e}")
            await query.message.reply_text("⚠️ حصل خطأ")
    
    elif query.data == "top":
        try:
            res = supabase.table('users').select('username, purchased, earned').order('earned', desc=True).limit(10).execute()
            if not res.data:
                await query.message.reply_text("لا يوجد لاعبين لسه")
                return
            text = "🏆 أعلى 10 لاعبين:\n\n"
            medals = ['🥇', '🥈', '🥉']
            for i, u in enumerate(res.data):
                medal = medals[i] if i < 3 else f"{i+1}."
                name = u.get('username', 'مجهول')
                points = (u.get('purchased', 0) or 0) + (u.get('earned', 0) or 0)
                text += f"{medal} {name} — {points} نقطة\n"
            await query.message.reply_text(text)
        except Exception as e:
            logger.error(f"top button error: {e}")
            await query.message.reply_text("⚠️ حصل خطأ")
    
    elif query.data == "myref":
        text = f"👥 نظام الإحالة\n\n💰 كل صديق = 5 جنيه\n\nكودك: {REFERRAL_CODE}\n\n{GAME_URL}"
        await query.message.reply_text(text)
    
    elif query.data == "bonus":
        code = f"NEON{datetime.now().strftime('%d%m')}"
        text = f"🎁 كود بونص النهاردة\n\n🎟️ الكود: {code}\n\nاكتبه في تبويب الأكواد في الموقع وهتاخد 10 نقاط\n\n⏰ صالح 24 ساعة"
        await query.message.reply_text(text)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")


def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN missing")
        return
    
    logger.info("Bot starting...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("top", top_players))
    app.add_handler(CommandHandler("bonus", bonus))
    app.add_handler(CommandHandler("myref", my_referral))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    
    logger.info("Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
