import telebot
import sql
from log import log
from constants import *
from config import TOKEN, CHAT
from time import sleep
import logging


bot = telebot.TeleBot(TOKEN)
logger = log('bot', 'bot.log', 'INFO')


@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, start_mess)
    logger.info(f"It's start handler. Message from {message.from_user.id}")


@bot.message_handler(commands=['help'])
def help_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, help_mess)
    logger.info(f"It's help handler. Message from {message.from_user.id}")


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message: telebot.types.Message):
    logger.info(f"It's sticker handler. Message from {message.from_user.id}")
    try:
        if message.chat.id == int(CHAT):
            bot.send_sticker(message.reply_to_message.forward_from.id, message.sticker.file_id)
            logger.info(f"In CHAT. Info: {message}")
        else:
            bot.forward_message(CHAT, message.chat.id, message.message_id)
            logger.info(f"Sticker handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.info(f"Exception in sticker handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['photo'])
def images_handler(message: telebot.types.Message):
    logger.info(f"It's images handler. Message from {message.from_user.id}")
    try:
        if message.chat.id == int(CHAT):
            bot.send_photo(message.reply_to_message.forward_from.id, message.photo[-1].file_id)
            logger.info(f"In CHAT. Info: {message}")
        else:
            bot.forward_message(CHAT, message.chat.id, message.message_id)
            logger.info(f"Image handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.info(f"Exception in image handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['document'])
def file_handler(message: telebot.types.Message):
    logger.info(f"It's file handler. Message from {message.from_user.id}")
    try:
        if message.chat.id == int(CHAT):
            bot.send_document(message.reply_to_message.forward_from.id, message.document.file_id)
            logger.info(f"In CHAT. Info: {message}")
        else:
            bot.forward_message(CHAT, message.chat.id, message.message_id)
            logger.info(f"File handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.info(f"Exception in file handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['audio'])
def audio_handler(message: telebot.types.Message):
    logger.info(f"It's audio handler. Message from {message.from_user.id}")
    try:
        if message.chat.id == int(CHAT):
            bot.send_audio(message.reply_to_message.forward_from.id, message.audio.file_id)
            logger.info(f"In CHAT. Info: {message}")
        else:
            bot.forward_message(CHAT, message.chat.id, message.message_id)
            logger.info(f"Audio handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.info(f"Exception in audio handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['voice'])
def voice_handler(message: telebot.types.Message):
    logger.info(f"It's voice handler. Message from {message.from_user.id}")
    try:
        if message.chat.id == int(CHAT):
            bot.send_voice(message.reply_to_message.forward_from.id, message.voice.file_id)
            logger.info(f"In CHAT. Info: {message}")
        else:
            bot.forward_message(CHAT, message.chat.id, message.message_id)
            logger.info(f"Voice handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.info(f"Exception in voice handler. Info: {error.with_traceback(None)}")


@bot.message_handler(func=lambda message: True)
def text_handler(message: telebot.types.Message):
    logger.info(f"It's text handler. Message from {message.from_user.id}")
    try:
        if message.chat.id == int(CHAT):
            bot.send_message(message.reply_to_message.forward_from.id, message.text)
            logger.info(f"In CHAT. Info: {message}")
        else:
            bot.forward_message(CHAT, message.chat.id, message.message_id)
            logger.info(f"Text handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.info(f"Exception in text handler. Info: {error.with_traceback(None)}")


def create_bot_instance(use_webhook=True, logging_enable=True, webhook_data=dict):
    if logging_enable:
        telebot.logger.setLevel(logging.getLevelName('DEBUG'))

    if use_webhook:
        bot.remove_webhook()
        sleep(1)
        bot.set_webhook(url=None, certificate=None)

    return bot
