import asyncio
import re
from telethon import TelegramClient, events
from telethon.errors import UsernameNotOccupiedError
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from bot_config import api_id, api_hash, phone_number, bot_token, admin_id, channel_destination
from database_bot import (
    setup_db,
    update_offsets,
    get_offsets,
    update_source_channel,
    get_source_channel,
    get_source_channel_id,
    set_enabled,
    is_enabled,
    set_price_adjustments,
    get_price_adjustments,
)
import nest_asyncio

nest_asyncio.apply()

user_client = TelegramClient("userbot_session", api_id, api_hash)
application = None

current_action = {}

manual_price_steps = [
    "buy_extra_gram",
    "buy_extra_misqal",
    "sell_reduce_gram",
    "sell_reduce_misqal",
    "dollar_price",
    "ounce_price",
    "global_misqal_price",
]

manual_prices = {}

async def resolve_channel_id(username):
    try:
        entity = await user_client.get_entity(username)
        return entity.id
    except UsernameNotOccupiedError:
        print("❌ یوزرنیم پیدا نشد")
        return None
    except Exception as e:
        print(f"❌ خطا در گرفتن آیدی کانال: {e}")
        return None



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != admin_id:
        await update.message.reply_text("You are not authorized.")
        return

    keyboard = [
        [KeyboardButton("🔛 روشن کردن ربات"), KeyboardButton("🔇 خاموش کردن ربات")],
        [KeyboardButton("تعیین افزوده خرید از ما (مثقال)"), KeyboardButton("تعیین افزوده خرید از ما (گرم)")],
        [KeyboardButton("تعیین کاهش فروش به ما (مثقال)"), KeyboardButton("تعیین کاهش فروش به ما (گرم)")],
        [KeyboardButton("📡 تنظیم کانال منبع")],
        [KeyboardButton("💰 قیمت‌گذاری دستی")],  # دکمه جدید
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "مدیریت تنظیمات ربات 🛠️", reply_markup=markup
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id != admin_id:
        await update.message.reply_text("You are not authorized.")
        return

    if text == "🔛 روشن کردن ربات":
        await set_enabled(True)
        await update.message.reply_text("✅ ربات فعال شد.")

    elif text == "🔇 خاموش کردن ربات":
        await set_enabled(False)
        await update.message.reply_text("⛔ ربات غیرفعال شد.")

    elif text == "📡 تنظیم کانال منبع":
        current_action[user_id] = "set_source_channel"
        await update.message.reply_text("لطفاً @username کانال منبع را ارسال کنید:")

    elif text == "تعیین افزوده خرید از ما (مثقال)":
        current_action[user_id] = "buy_misqal"
        await update.message.reply_text("مقدار افزوده خرید (مثقال) را وارد کنید:")

    elif text == "تعیین افزوده خرید از ما (گرم)":
        current_action[user_id] = "buy_gram"
        await update.message.reply_text("مقدار افزوده خرید (گرم) را وارد کنید:")

    elif text == "تعیین کاهش فروش به ما (مثقال)":
        current_action[user_id] = "sell_misqal"
        await update.message.reply_text("مقدار کاهنده فروش (مثقال) را وارد کنید:")

    elif text == "تعیین کاهش فروش به ما (گرم)":
        current_action[user_id] = "sell_gram"
        await update.message.reply_text("مقدار کاهنده فروش (گرم) را وارد کنید:")

    elif text == "💰 قیمت‌گذاری دستی":
        current_action[user_id] = "manual_pricing_step"
        manual_prices[user_id] = {}
        await update.message.reply_text("لطفاً قیمت افزوده خرید از ما (گرم) را وارد کنید:")

    elif user_id in current_action:
        action = current_action[user_id]

        if action == "set_source_channel":
            current_action.pop(user_id)
            chat_id = await resolve_channel_id(text)
            if chat_id:
                await update_source_channel(text.lower(), chat_id)
                await update.message.reply_text(f"✅ کانال منبع تنظیم شد: {text}")
            else:
                await update.message.reply_text("❌ کانال یافت نشد. لطفاً دوباره تلاش کنید.")

        elif action == "buy_misqal":
            current_action.pop(user_id)
            value = text.replace(",", "")
            if value.isdigit():
                val = int(value)
                bm, bg, sm, sg = await get_price_adjustments()
                await set_price_adjustments(val, bg, sm, sg)
                await update.message.reply_text("✅ مقدار با موفقیت ثبت شد.")
            else:
                await update.message.reply_text("لطفاً فقط عدد وارد کنید.")

        elif action == "buy_gram":
            current_action.pop(user_id)
            value = text.replace(",", "")
            if value.isdigit():
                val = int(value)
                bm, bg, sm, sg = await get_price_adjustments()
                await set_price_adjustments(bm, val, sm, sg)
                await update.message.reply_text("✅ مقدار با موفقیت ثبت شد.")
            else:
                await update.message.reply_text("لطفاً فقط عدد وارد کنید.")

        elif action == "sell_misqal":
            current_action.pop(user_id)
            value = text.replace(",", "")
            if value.isdigit():
                val = int(value)
                bm, bg, sm, sg = await get_price_adjustments()
                await set_price_adjustments(bm, bg, val, sg)
                await update.message.reply_text("✅ مقدار با موفقیت ثبت شد.")
            else:
                await update.message.reply_text("لطفاً فقط عدد وارد کنید.")

        elif action == "sell_gram":
            current_action.pop(user_id)
            value = text.replace(",", "")
            if value.isdigit():
                val = int(value)
                bm, bg, sm, sg = await get_price_adjustments()
                await set_price_adjustments(bm, bg, sm, val)
                await update.message.reply_text("✅ مقدار با موفقیت ثبت شد.")
            else:
                await update.message.reply_text("لطفاً فقط عدد وارد کنید.")

        elif action == "manual_pricing_step":
            value = text.replace(",", "").strip()
            step_index = len(manual_prices.get(user_id, {}))
            current_step = manual_price_steps[step_index]

            # اعتبارسنجی مقدار ورودی
            if current_step in ["dollar_price", "ounce_price", "global_misqal_price"]:
                try:
                    val = float(value)
                except:
                    await update.message.reply_text("لطفاً یک عدد معتبر وارد کنید.")
                    return
            else:
                if not value.isdigit():
                    await update.message.reply_text("لطفاً فقط عدد صحیح وارد کنید.")
                    return
                val = int(value)

            manual_prices.setdefault(user_id, {})[current_step] = val

            if step_index + 1 < len(manual_price_steps):
                next_step = manual_price_steps[step_index + 1]
                step_texts = {
                    "buy_extra_gram": "لطفاً قیمت افزوده خرید از ما (گرم) را وارد کنید:",
                    "buy_extra_misqal": "لطفاً قیمت افزوده خرید از ما (مثقال) را وارد کنید:",
                    "sell_reduce_gram": "لطفاً قیمت کاهش فروش به ما (گرم) را وارد کنید:",
                    "sell_reduce_misqal": "لطفاً قیمت کاهش فروش به ما (مثقال) را وارد کنید:",
                    "dollar_price": "قیمت دلار آزاد را وارد کنید:",
                    "ounce_price": "قیمت اونس طلا را وارد کنید:",
                    "global_misqal_price": "لطفاً قیمت مثقال جهانی را وارد کنید:",
                }
                await update.message.reply_text(step_texts[next_step])
            else:
                prices = manual_prices[user_id]

                header = " نرخ مرجع اتحادیه طلا و جواهرتبریز\n\n"

                footer = (
                    "\nمعاملات:⬇️\n\n"
                    "📞 0914-130-7990\n"
                    "☎️ 041-4312-2470\n\n"
                    "ارتباط با حسابداری: @atlasgold2470\n\n"
                    "       🔱 مظنه آبشده وظیفه 🔱\n"
                    "             گالری طلای اطلس"
                )

                final_text = (
                    f"{header}"
                    f"🟢 خرید از ما:\n"
                    f"هر مثقال: {prices['buy_extra_misqal']:,} تومان\n"
                    f"هر گرم: {prices['buy_extra_gram']:,} تومان\n\n"
                    f"🔴 فروش به ما:\n"
                    f"هر مثقال: {prices['sell_reduce_misqal']:,} تومان\n"
                    f"هر گرم: {prices['sell_reduce_gram']:,} تومان\n\n"
                    f"💵 دلار آزاد: {prices['dollar_price']:,} تومان\n"
                    f"💰 اونس طلا: {prices['ounce_price']:,} دلار\n"
                    f"🌎 مثقال جهانی: {prices['global_misqal_price']:,} تومان\n"
                    f"{footer}"
                )

                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("تایید ارسال به کانال", callback_data="confirm_manual_send")]]
                )

                await update.message.reply_text(final_text, reply_markup=keyboard)

                current_action.pop(user_id)
                manual_prices.pop(user_id)

        else:
            await update.message.reply_text("دستور نامعتبر.")
            current_action.pop(user_id)

    else:
        await update.message.reply_text("دستور نامعتبر.")

async def handle_confirm_manual_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id != admin_id:
        await query.edit_message_text("شما اجازه ارسال پیام به کانال را ندارید.")
        return

    message_text = query.message.text
    await send_message_to_destination(message_text)

    await query.edit_message_text("✅ پیام با موفقیت به کانال ارسال شد.")

async def send_message_to_destination(text):
    global application
    if application is None:
        print("Application not ready yet!")
        return
    try:
        await application.bot.send_message(chat_id=channel_destination, text=text)
    except Exception as e:
        print(f"Error sending message: {e}")

@user_client.on(events.NewMessage)
async def handler(event):
    if not await is_enabled():
        return

    source_channel_id = await get_source_channel_id()
    source_channel_username = await get_source_channel()
    if not source_channel_id and not source_channel_username:
        return

    if event.chat and ((source_channel_id and event.chat.id == source_channel_id) or
                       (source_channel_username and event.chat.username and
                        f"@{event.chat.username.lower()}" == source_channel_username.lower())):

        print(f"📥 پیام جدید از کانال مجاز: {event.chat.title} | ID: {event.chat.id} | username: @{getattr(event.chat, 'username', 'N/A')}")
        text = event.raw_text.strip()
        
        print("متن پیام دریافتی:")
        print(text)
        print("-------------------------")

        pattern_misqal_buy = r"🟢 خرید از ما:\s*\nهر مثقال:\s*([\d,]+) تومان"
        pattern_gram_buy = r"هر گرم:\s*([\d,]+) تومان"
        pattern_misqal_sell = r"🔴 فروش به ما:\s*\nهر مثقال:\s*([\d,]+) تومان"
        pattern_gram_sell = r"هر گرم:\s*([\d,]+) تومان"

        def parse_number(s):
            return int(s.replace(",", ""))

        buy_misqal = None
        buy_gram = None
        sell_misqal = None
        sell_gram = None

        m = re.search(pattern_misqal_buy, text)
        if m:
            buy_misqal = parse_number(m.group(1))

        m = re.search(pattern_gram_buy, text)
        if m:
            buy_gram = parse_number(m.group(1))

        m = re.search(pattern_misqal_sell, text)
        if m:
            sell_misqal = parse_number(m.group(1))

        m = re.search(pattern_gram_sell, text)
        if m:
            sell_gram = parse_number(m.group(1))

        if None in (buy_misqal, buy_gram, sell_misqal, sell_gram):
            print("قیمت‌ها ناقص بودند، پیام رد شد.")
            return

        buy_extra_misqal, buy_extra_gram, sell_reduce_misqal, sell_reduce_gram = await get_price_adjustments()

        buy_misqal += buy_extra_misqal
        buy_gram += buy_extra_gram
        sell_misqal -= sell_reduce_misqal
        sell_gram -= sell_reduce_gram

        pattern_dollar = r"💵 دلار آزاد:\s*([\d,]+) تومان"
        pattern_ounce = r"💰 اونس طلا:\s*([\d,.]+) دلار"
        pattern_global_misqal = r"🌎 مثقال جهانی:\s*([\d,]+) تومان"

        dollar = "نامشخص"
        ounce = "نامشخص"
        global_misqal = "نامشخص"

        m = re.search(pattern_dollar, text)
        if m:
            dollar = m.group(1)

        m = re.search(pattern_ounce, text)
        if m:
            ounce = m.group(1)

        m = re.search(pattern_global_misqal, text)
        if m:
            global_misqal = m.group(1)

        footer = """
معاملات:⬇️

📞0914-130-7990
☎️041- 4312-2470

ارتباط با حسابداری @atlasgold2470

       🔱مظنه آبشده وظیفه🔱 
             گالری طلای اطلس
"""
        header = " نرخ مرجع اتحادیه طلا و جواهرتبریز\n\n"
        
        final_text = (
            f"{header}"
            f"🟢 خرید از ما: \n"
            f"هر مثقال: {buy_misqal:,} تومان\n"
            f"هر گرم: {buy_gram:,} تومان\n\n"
            f"🔴 فروش به ما: \n"
            f"هر مثقال: {sell_misqal:,} تومان\n"
            f"هر گرم: {sell_gram:,} تومان\n\n"
            f"💵 دلار آزاد: {dollar} تومان\n"
            f"💰 اونس طلا: {ounce} دلار\n"
            f"🌎 مثقال جهانی: {global_misqal} تومان\n"
            f"{footer}"
        )

        await send_message_to_destination(final_text)
        print("✅ پیام اصلاح شده ارسال شد.")

async def main():
    global application
    print("Starting...")
    await setup_db()

    await user_client.start(phone=phone_number)
    print("UserBot started.")

    application = ApplicationBuilder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_buttons))
    application.add_handler(CallbackQueryHandler(handle_confirm_manual_send, pattern="confirm_manual_send"))

    print("Bot started.")

    await asyncio.gather(
        user_client.run_until_disconnected(),
        application.run_polling()
    )

if __name__ == "__main__":
    asyncio.run(main())
