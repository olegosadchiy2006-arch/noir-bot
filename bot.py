#!/usr/bin/env python3
"""
Telegram-бот для замовлення чорної сукні NOIR
Замовлення надсилаються адміністратору (ID: 706778814)
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# ── Налаштування ──────────────────────────────────────────
TOKEN = "8762049567:AAHdKLz878JlwySWPOmJGFNC6VHgqZYxvUs"
ADMIN_ID = 706778814  # ID брата — сюди надходять замовлення

# Кроки діалогу
NAME, PHONE, SIZE, CITY, NOVA_POSHTA, CONFIRM = range(6)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ── /start ────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👗 *Вітаємо у NOIR!*\n\n"
        "Ви оформлюєте замовлення на чорну сукню:\n"
        "• Міні, V-подібний виріз, об'ємні рукави\n"
        "• Ціна: ~~1300 грн~~ → *920 грн* (знижка 29%)\n\n"
        "Для скасування в будь-який момент натисніть /cancel\n\n"
        "Введіть ваше *П.І.Б.*:",
        parse_mode="Markdown"
    )
    return NAME


# ── Крок 1: ім'я ──────────────────────────────────────────
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(
        "📱 Введіть ваш *номер телефону*:\n_(наприклад: +380991234567)_",
        parse_mode="Markdown"
    )
    return PHONE


# ── Крок 2: телефон ───────────────────────────────────────
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text.strip()

    size_keyboard = ReplyKeyboardMarkup(
        [["42-44 / S/M", "46-48 / M/L"]],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text(
        "📏 Оберіть *розмір*:",
        reply_markup=size_keyboard,
        parse_mode="Markdown"
    )
    return SIZE


# ── Крок 3: розмір ────────────────────────────────────────
async def get_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    size = update.message.text.strip()
    if size not in ["42-44 / S/M", "46-48 / M/L"]:
        await update.message.reply_text("Будь ласка, оберіть розмір з кнопок нижче 👇")
        return SIZE
    context.user_data["size"] = size
    await update.message.reply_text(
        "🏙 Введіть ваше *місто*:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return CITY


# ── Крок 4: місто ─────────────────────────────────────────
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text.strip()
    await update.message.reply_text(
        "📦 Введіть *номер відділення Нової Пошти*:\n_(наприклад: 12)_",
        parse_mode="Markdown"
    )
    return NOVA_POSHTA


# ── Крок 5: відділення НП ─────────────────────────────────
async def get_nova_poshta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nova_poshta"] = update.message.text.strip()

    d = context.user_data
    summary = (
        f"📋 *Перевірте ваше замовлення:*\n\n"
        f"👤 П.І.Б.: {d['name']}\n"
        f"📱 Телефон: {d['phone']}\n"
        f"📏 Розмір: {d['size']}\n"
        f"🏙 Місто: {d['city']}\n"
        f"📦 Відділення НП: №{d['nova_poshta']}\n"
        f"💰 Сума: *920 грн*\n\n"
        f"Все вірно?"
    )

    confirm_keyboard = ReplyKeyboardMarkup(
        [["✅ Підтвердити замовлення", "❌ Скасувати"]],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text(
        summary,
        reply_markup=confirm_keyboard,
        parse_mode="Markdown"
    )
    return CONFIRM


# ── Крок 6: підтвердження ─────────────────────────────────
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "Підтвердити" in text:
        d = context.user_data
        user = update.effective_user
        username = f"@{user.username}" if user.username else "немає username"

        # Повідомлення адміністратору
        admin_msg = (
            f"🛍 *НОВЕ ЗАМОВЛЕННЯ — NOIR*\n"
            f"{'─' * 30}\n"
            f"👤 П.І.Б.: {d['name']}\n"
            f"📱 Телефон: {d['phone']}\n"
            f"📏 Розмір: {d['size']}\n"
            f"🏙 Місто: {d['city']}\n"
            f"📦 Відділення НП: №{d['nova_poshta']}\n"
            f"💰 Сума: *920 грн*\n"
            f"{'─' * 30}\n"
            f"🔗 Telegram: {username}\n"
            f"🆔 ID: `{user.id}`"
        )

        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Не вдалося надіслати адміністратору: {e}")

        # Відповідь клієнту
        await update.message.reply_text(
            "✅ *Дякуємо за замовлення!*\n\n"
            "Ми отримали ваше замовлення і зв'яжемося з вами найближчим часом 🖤\n\n"
            "Якщо є питання — пишіть у Instagram або Telegram:\n"
            "📸 @polin.style.ua",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            "❌ Замовлення скасовано.\n\nНатисніть /start щоб почати знову.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


# ── /cancel ───────────────────────────────────────────────
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Оформлення скасовано.\n\nНатисніть /start щоб почати знову.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ── Запуск ────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SIZE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_size)],
            CITY:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            NOVA_POSHTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nova_poshta)],
            CONFIRM:     [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("🤖 Бот NOIR запущено! Натисніть Ctrl+C для зупинки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
