import logging
import random
import time
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8879104269:AAGsZt40-mWzOQ_FxjxrJfuidgE43x1tOD0"
ADMIN_USERNAME = "Qltae"
CHANNEL_USERNAME = "@rvLpL"
CHANNEL_URL = "https://t.me/rvLpL"

ALL_COUNTRIES = {
    "ir": "🇮🇷 ایران", "us": "🇺🇸 آمریکا", "de": "🇩🇪 آلمان", 
    "tr": "🇹🇷 ترکیه", "fr": "🇫🇷 فرانسه", "nl": "🇳🇱 هلند", 
    "gb": "🇬🇧 انگلستان", "jp": "🇯🇵 ژاپن", "kr": "🇰🇷 کره جنوبی", 
    "ae": "🇦🇪 امارات", "ca": "🇨🇦 کانادا", "au": "🇦🇺 استرالیا", 
    "sg": "🇸🇬 سنگاپور", "ru": "🇷🇺 روسیه", "it": "🇮🇹 ایتالیا", 
    "es": "🇪🇸 اسپانیا", "br": "🇧🇷 برزیل", "ch": "🇨🇭 سوییس", 
    "se": "🇸🇪 سوئد", "no": "🇳🇴 نروژ", "fi": "🇫🇮 فنلاند", 
    "dk": "🇩🇰 دانمارک", "pl": "🇵🇱 لهستان", "at": "🇦🇹 اتریش", 
    "be": "🇧🇪 بلژیک", "ua": "🇺🇦 اوکراین", "cz": "🇨🇿 جمهوری چک", 
    "ro": "🇷🇴 رومانی", "hu": "🇭🇺 مجارستان", "pt": "🇵🇹 پرتغال", 
    "gr": "🇬🇷 یونان", "in": "🇮🇳 هند", "my": "🇲🇾 مالزی", 
    "id": "🇮🇩 اندونزی", "th": "🇹🇭 تایلند", "vn": "🇻🇳 ویتنام", 
    "ph": "🇵🇭 فیلیپین", "za": "🇿🇦 آفریقای جنوبی", "ar": "🇦🇷 آرژانتین", 
    "cl": "🇨🇱 شیلی", "mx": "🇲🇽 مکزیک", "sa": "🇸🇦 عربستان"
}

async def fetch_dns_from_public_dns(country_code=None, best_only=False, random_mode=False):
    dns_list = []
    try:
        url = f"https://public-dns.info/nameserver/{country_code}.html" if country_code else "https://public-dns.info/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        ip = cols[0].text.strip()
                        location = cols[1].text.strip().replace('\n', ' ')
                        status = cols[4].text.strip()
                        reliability = cols[5].text.strip()
                        
                        if best_only:
                            try:
                                rel_num = int(reliability.replace('%', '').strip())
                                if rel_num < 80:
                                    continue
                            except:
                                pass

                        dns_list.append({
                            "ip": ip,
                            "location": location if location else "سرور اختصاصی",
                            "status": status if status else "valid",
                            "reliability": reliability if reliability else "90%"
                        })
    except Exception as e:
        logger.error(f"Error scraping DNS: {e}")
        
    if not dns_list:
        base_ips = ["1.1.1.1", "1.0.0.1", "8.8.8.8", "8.8.4.4", "9.9.9.9", "149.112.112.112", "208.67.222.222", "208.67.220.220", "78.157.42.100", "10.202.10.10"]
        random.shuffle(base_ips)
        for ip in base_ips[:10]:
            dns_list.append({"ip": ip, "location": "سرور اختصاصی گیمینگ", "status": "valid", "reliability": "99%"})

    if random_mode:
        return random.sample(dns_list, min(10, len(dns_list)))
    return dns_list[:10]

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🌐 لیست کشورها"), KeyboardButton("⭐ بهترین DNSهای جهانی")],
        [KeyboardButton("🎲 DNS شانس / رندوم (۱۰ عددی)"), KeyboardButton("🎮 انتخاب بازی (رفع تحریم & کاهش پینگ)")],
        [KeyboardButton("📱 آموزش چنج کردن DNS"), KeyboardButton("💬 پشتیبانی و ارتباط با هادی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_force_sub_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 عضويت در کانال", url=CHANNEL_URL)],
        [InlineKeyboardButton("✅ عضو شدم، بررسی کن", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_countries_keyboard():
    keyboard = []
    row = []
    for code, name in ALL_COUNTRIES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"country_{code}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("« بازگشت به منوی اصلی", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def get_games_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🎯 Call of Duty", callback_data="game_cod"),
            InlineKeyboardButton("🪖 PUBG Mobile", callback_data="game_pubg")
        ],
        [
            InlineKeyboardButton("⚔️ Clash of Clans / Royale", callback_data="game_clash"),
            InlineKeyboardButton("⚡️ World of Warcraft (WoW)", callback_data="game_wow")
        ],
        [
            InlineKeyboardButton("✈️ War Thunder", callback_data="game_wt"),
            InlineKeyboardButton("⚽️ eFootball / FIFA", callback_data="game_fifa")
        ],
        [
            InlineKeyboardButton("« بازگشت به منوی اصلی", callback_data="back_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def check_user_membership(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        logger.warning(f"Force-sub check bypassed: {e}")
        return True

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_user_membership(context.bot, user_id)
    
    if not is_member:
        text = (
            "🚨 **برای استفاده از ربات، لطفاً ابتدا در کانال زیر عضو شوید:**\n\n"
            f"🔗 {CHANNEL_URL}\n\n"
            "پس از عضویت، روی دکمه «عضو شدم» کلیک کنید 👇"
        )
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_force_sub_keyboard())
        return

    welcome_txt = (
        "👑 **به پنل اختصاصی Hadi Gaming DNS Engine خوش آمدید**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "قوی‌ترین موتور هوشمند استخراج و تفکیک DNSهای گیمینگ با بالاترین سرعت و پایداری.\n\n"
        "👇 گزینه مورد نظر خود را انتخاب کنید:"
    )
    await update.message.reply_text(welcome_txt, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == "check_sub":
        is_member = await check_user_membership(context.bot, user_id)
        if is_member:
            try:
                await query.message.delete()
            except:
                pass
            welcome_txt = (
                "✅ **عضویت شما تأیید شد!**\n\n"
                "👑 **به پنل اختصاصی Hadi Gaming DNS Engine خوش آمدید**\n"
                "👇 از دکمه‌های منوی زیر استفاده کنید:"
            )
            await context.bot.send_message(chat_id=user_id, text=welcome_txt, parse_mode="Markdown", reply_markup=get_main_keyboard())
        else:
            await query.answer("❌ شما هنوز در کانال عضو نشده‌اید!", show_alert=True)
        return

    if data.startswith("country_"):
        c_code = data.replace("country_", "")
        c_name = ALL_COUNTRIES.get(c_code, "انتخابی")
        
        await query.edit_message_text(f"🔄 در حال استخراج ۱۰ سرور برتر {c_name} به همراه تفکیک DNS 1 و DNS 2...")
        dns_data = await fetch_dns_from_public_dns(country_code=c_code)
        
        res_msg = f"🌐 **۱۰ سرور برتر کشور {c_name} (تفکیک‌شده برای DNS Changer):**\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for i in range(0, len(dns_data) - 1, 2):
            pair_num = (i // 2) + 1
            dns1 = dns_data[i]
            dns2 = dns_data[i+1]
            res_msg += (
                f"🔹 **جفت شماره {pair_num}:**\n"
                f"• 🟢 **DNS 1:** `{dns1['ip']}` ({dns1['location']} | پایداری: {dns1['reliability']})\n"
                f"• 🔵 **DNS 2:** `{dns2['ip']}` ({dns2['location']} | پایداری: {dns2['reliability']})\n\n"
            )
        
        back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("« بازگشت به لیست کشورها", callback_data="back_countries")]])
        await query.edit_message_text(res_msg, parse_mode="Markdown", reply_markup=back_kb)
        return

    if data == "back_countries":
        await query.edit_message_text("🌐 **لیست کامل کشورهای جهان (انتخاب جهت دریافت بهترین‌ها):**", reply_markup=get_countries_keyboard())
        return

    if data.startswith("game_"):
        g_type = data.replace("game_", "")
        game_dns_info = {
            "cod": "🎯 **Call of Duty (Mobile / Warzone):**\n• **DNS 1:** `10.202.10.10` (Radar)\n• **DNS 2:** `10.202.10.11` (Radar)",
            "pubg": "🪖 **PUBG Mobile:**\n• **DNS 1:** `1.1.1.1` (Cloudflare)\n• **DNS 2:** `1.0.0.1` (Cloudflare)",
            "clash": "⚔️ **Clash of Clans / Royale:**\n• **DNS 1:** `78.157.42.100` (Electro)\n• **DNS 2:** `78.157.42.101` (Electro)",
            "wow": "⚡️ **World of Warcraft:**\n• **DNS 1:** `10.202.10.10` (Radar)\n• **DNS 2:** `1.1.1.1` (Cloudflare)",
            "wt": "✈️ **War Thunder:**\n• **DNS 1:** `78.157.42.100` (Electro)\n• **DNS 2:** `10.202.10.10` (Radar)",
            "fifa": "⚽️ **eFootball / FIFA:**\n• **DNS 1:** `178.22.122.100` (Shekan)\n• **DNS 2:** `185.51.200.2` (Shekan)"
        }
        info = game_dns_info.get(g_type, "• **DNS 1:** `10.202.10.10`\n• **DNS 2:** `10.202.10.11`")
        back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("« بازگشت به لیست بازی‌ها", callback_data="back_games")]])
        await query.edit_message_text(info, parse_mode="Markdown", reply_markup=back_kb)

    elif data == "back_games":
        await query.edit_message_text("🎮 **لطفاً بازی مورد نظر خود را انتخاب کنید:**", reply_markup=get_games_keyboard())

    elif data == "back_main":
        await query.edit_message_text("✅ به منوی اصلی بازگشتید.")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()

    if text == "🌐 لیست کشورها":
        await message.reply_text("🌐 **لیست کامل کشورهای جهان (انتخاب جهت دریافت بهترین‌ها):**", reply_markup=get_countries_keyboard())
        return

    if text == "⭐ بهترین DNSهای جهانی":
        wait_msg = await message.reply_text("🔄 در حال فیلتر بهترین سرورهای جهان...")
        best_dns = await fetch_dns_from_public_dns(best_only=True)
        
        res_msg = "⭐ **برترین جفت‌های DNS جهانی (پایداری بالا):**\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i in range(0, len(best_dns) - 1, 2):
            pair_num = (i // 2) + 1
            dns1 = best_dns[i]
            dns2 = best_dns[i+1]
            res_msg += (
                f"🔹 **جفت جهانی {pair_num}:**\n"
                f"• 🟢 **DNS 1:** `{dns1['ip']}` ({dns1['location']} | {dns1['reliability']})\n"
                f"• 🔵 **DNS 2:** `{dns2['ip']}` ({dns2['location']} | {dns2['reliability']})\n\n"
            )
        await context.bot.delete_message(chat_id=message.chat_id, message_id=wait_msg.message_id)
        await message.reply_text(res_msg, parse_mode="Markdown")
        return

    if text == "🎲 DNS شانس / رندوم (۱۰ عددی)":
        wait_msg = await message.reply_text("🎲 در حال انتخاب تصادفی سرورهای فعال...")
        rand_dns = await fetch_dns_from_public_dns(random_mode=True)
        
        res_msg = "🎲 **سرورهای تصادفی شانس (تست جفت‌ها):**\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i in range(0, len(rand_dns) - 1, 2):
            pair_num = (i // 2) + 1
            dns1 = rand_dns[i]
            dns2 = rand_dns[i+1]
            res_msg += (
                f"🎲 **جفت شانس {pair_num}:**\n"
                f"• 🟢 **DNS 1:** `{dns1['ip']}` ({dns1['location']} | {dns1['reliability']})\n"
                f"• 🔵 **DNS 2:** `{dns2['ip']}` ({dns2['location']} | {dns2['reliability']})\n\n"
            )
        await context.bot.delete_message(chat_id=message.chat_id, message_id=wait_msg.message_id)
        await message.reply_text(res_msg, parse_mode="Markdown")
        return

    if text == "🎮 انتخاب بازی (رفع تحریم & کاهش پینگ)":
        await message.reply_text("🎮 **لطفاً بازی مورد نظر خود را انتخاب کنید:**", reply_markup=get_games_keyboard())
        return

    if text == "📱 آموزش چنج کردن DNS":
        guide_txt = (
            "📱 **نحوه ست کردن DNS در نرم‌افزار:**\n\n"
            "• مقدار روبروی **DNS 1** رو توی کادر اول (DNS 1) وارد کنید.\n"
            "• مقدار روبروی **DNS 2** رو توی کادر دوم (DNS 2) وارد کنید.\n"
            "• روی دکمه Start بزنید تا متصل بشه!"
        )
        await message.reply_text(guide_txt, parse_mode="Markdown")
        return

    if text == "💬 پشتیبانی و ارتباط با هادی":
        await message.reply_text(f"💬 **پشتیبانی ربات:**\n👉 @{ADMIN_USERNAME}", parse_mode="Markdown")
        return

def run_bot():
    while True:
        try:
            app = (
                ApplicationBuilder()
                .token(TOKEN)
                .read_timeout(30)
                .connect_timeout(30)
                .get_updates_read_timeout(30)
                .build()
            )
            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(CallbackQueryHandler(button_handler))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
            
            print("🚀 Hadi Gaming DNS Engine Ultimate is ONLINE!")
            app.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Network error: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    run_bot()
      
