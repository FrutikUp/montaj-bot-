"""
Telegram Bot: калькулятор-смета (цены из Google Sheets, публичная таблица).
Зависимости:
  pip install python-telegram-bot==20.5 requests
(версия PTB 20+; если используешь другую версию — возможно небольшие правки)

Как использовать:
  1) Вставь TELEGRAM_TOKEN = "твой токен"
  2) Вставь GOOGLE_SHEET_LINK = "ссылка на публичную Google Sheet (View access)"
  3) Запусти: python bot.py
"""

import logging
import requests
import csv
import io
from typing import Dict, List, Tuple
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    InputFile,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

