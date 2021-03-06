import telebot
from helpers import sql
from helpers.log import log
from helpers.constants import *
from config import TOKEN, CHAT
from helpers.forward import Forward
from helpers.cache import Cache
from helpers.utils import send_to_chat, check_for_admin
import logging
import json
import os


bot = telebot.TeleBot(TOKEN)
logger = log('bot', 'bot.log', 'INFO')
hidden_forward = Forward(False)
bot_cache = Cache(True)


@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message):
    adding = sql.add_user(
        message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
    if not adding:
        logger.error(f"Error in start handler! User {message.from_user.id} did not have added to the bot")
        return
    bot.send_message(message.from_user.id, start_mess)
    bot_cache.update_user_count()
    logger.info(f"It's start handler. User {message.from_user.id} had added to the bot")


@bot.message_handler(commands=['help'])
def help_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, help_mess)
    logger.info(f"It's help handler. Message from user {message.from_user.id}")


# *************************************************** Admin's panel ***************************************************
# *********************************************************************************************************************
@bot.message_handler(commands=['helping'])
def helping_handler(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /helping command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to send /helping command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        bot.send_message(message.from_user.id, helping_mess)
        logger.info(f"It's helping handler. Message from user {message.from_user.id}")


@bot.message_handler(commands=['usercount'])
def get_user_count(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /usercount command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to sent /usercount command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        user_count = bot_cache.user_count()
        if not user_count:
            bot.send_message(message.from_user.id, user_count_error)
            logger.info(f"Error getting user's count. User which to sent /usercount command: {message.from_user.id}")
            return
        bot.send_message(message.from_user.id, count_mess.format(user_count))
        logger.info(f"User {message.from_user.id} had gotten user's count. Result: {user_count}")


@bot.message_handler(commands=['global'])
def global_mailing(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /global command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to send /global command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        text = (message.text[7:]).strip()
        if text == '':
            bot.send_message(message.from_user.id, global_error)
            logger.info(f"Error global mailing. User {message.from_user.id} doesn't send a text")
            return
        deleted_user = 0
        users = sql.get_users()
        if not users:
            bot.send_message(message.from_user.id, get_user_error)
            logger.info(f"Error getting list of users. User which to send /global command: {message.from_user.id}")
            return
        for user in users:
            try:
                bot.send_message(user, text, reply_markup='HTML')
                logger.info(f"User {user} is using the bot. A message had sent successfully")
            except Exception as error:
                deleted_user += 1
                logger.error(f"User {user} is'nt using the bot. "
                             f"Error in global mailing function: {error.with_traceback(None)}")
        bot.send_message(message.from_user.id, deleted_mess.format(deleted_user))
        logger.info(f"User {message.from_user.id} had sent global mailing. Text: {text}. Deleted user: {deleted_user}")


@bot.message_handler(commands=['getfullcache'])
def get_cache(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /getfullcache command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to send /getfullcache command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        try:
            if not os.path.exists('cache/'):
                os.mkdir('./cache/')
            with open('./cache/cache.txt', 'w', encoding='utf8') as cache:
                json.dump(hidden_forward.message_forward_data, cache, ensure_ascii=False, indent=2)
            doc = open('./cache/cache.txt', 'rb')
            bot.send_document(message.from_user.id, doc)
            doc.close()
            logger.info(
                f"User {message.from_user.id} had gotten cache data. Result: {hidden_forward.message_forward_data}")
        except Exception as error:
            logger.error(error.with_traceback(None))


@bot.message_handler(commands=['getlogs'])
def get_logs(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /getlogs command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to send /getlogs command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        try:
            if not os.path.exists('logs/'):
                return
            file_list = os.listdir('logs/')
            for file in file_list:
                try:
                    doc = open(f'logs/{file}', 'rb')
                    bot.send_document(message.from_user.id, doc)
                    doc.close()
                except Exception as error:
                    bot.send_message(message.from_user.id, f'File {file} is empty!')
                    logger.warning(f'File {file} is empty. Error: {error}. User id {message.from_user.id}')
            logger.info(f"User {message.from_user.id} had gotten logs. Result: {hidden_forward.message_forward_data}")
        except Exception as error:
            logger.error(error.with_traceback(None))


@bot.message_handler(commands=['banuser'])
def ban_user(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /banuser command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to send /banuser command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        user_id = message.text[8:].strip()
        if len(user_id) == 0:
            bot.send_message(message.from_user.id, enter_id_error)
            logger.error(f'Error enter an user id for ban. Id is not defined!')
            return
        result = sql.ban_user(int(user_id))
        if not result:
            bot.send_message(message.from_user.id, add_ban_error)
            logger.error(
                'Error adding an user to ban list. User is on of admins or the user in list already or '
                'this is other error with DB')
            return
        if len(result) == 0:
            bot.send_message(message.from_user.id, clear_ban_mess)
        else:
            bot.send_message(message.from_user.id, str(result))
        bot_cache.update_user_ban_list(result)
        logger.info(f"User {message.from_user.id} had added a user at ban. Bans list: {result}")


@bot.message_handler(commands=['unbanuser'])
def un_ban_user(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /unbanuser command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to send /unbanuser command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        user_id = message.text[10:].strip()
        if len(user_id) == 0:
            bot.send_message(message.from_user.id, enter_id_error)
            logger.error(f'Error enter an user id for deleted from ban. Id is not defined!')
            return
        result = sql.un_ban(int(user_id))
        if not result:
            bot.send_message(message.from_user.id, un_ban_error)
            logger.error(
                'Error with delete an user from ban list. '
                'The user is not in ban list or this is other error with DB')
            return
        if len(result) == 0:
            bot.send_message(message.from_user.id, clear_ban_mess)
        else:
            bot.send_message(message.from_user.id, str(result))
        bot_cache.update_user_ban_list(result)
        logger.info(f"User {message.from_user.id} had removed a user at ban. Bans list: {result}")


'''
TODO: Have to add two new handlers: 
one for adding a new admin to DataBase and one for deleting a some admin from DataBase
'''


@bot.message_handler(commands=['addadmin'])
def add_admin(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /addadmin command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to send /addadmin command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        new_admin_id = message.text[10:].strip()
        if len(new_admin_id) == 0:
            bot.send_message(message.from_user.id, enter_id_error)
            logger.error(f'Error enter an user id for adding to admin list. Id is not defined!')
            return
        result = sql.add_admin(int(new_admin_id))
        if not result:
            bot.send_message(message.from_user.id, add_admin_error)
            logger.error('Error adding an user to admin list. User is an admins or this is other error with DB')
            return
        bot_cache.update_admins_list()
        bot.send_message(message.from_user.id, add_admin_mes)
        logger.info(f"User {message.from_user.id} had added a user to admin list.")


@bot.message_handler(commands=['deladmin'])
def delete_admin(message: telebot.types.Message):
    logger.info(f"User {message.from_user.id} had entered /deladmin command")
    admins = bot_cache.get_admins()
    if not admins:
        bot.send_message(message.from_user.id, get_admins_error)
        logger.info(f"Error getting list of admins. User which to send /deladmin command: {message.from_user.id}")
        return
    if check_for_admin(message, admins):
        new_admin_id = message.text[10:].strip()
        if len(new_admin_id) == 0:
            bot.send_message(message.from_user.id, enter_id_error)
            logger.error(f'Error enter an user id for deleting from admin list. Id is not defined!')
            return
        result = sql.delete_admin(int(new_admin_id))
        if not result:
            bot.send_message(message.from_user.id, delete_admin_mes)
            logger.error('Error deleting an user from admin list. User is an admins or this is other error with DB')
            return
        bot_cache.update_admins_list()
        bot.send_message(message.from_user.id, 'Some text about success!')
        logger.info(f"User {message.from_user.id} had deleted a user from admin list.")
# *********************************************************************************************************************
# *********************************************************************************************************************


@bot.message_handler(func=lambda message: message.from_user.id in bot_cache.get_ban_list())
def send_ban_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, ban_mess)
    logger.info(f"It's help send_ban_handler. Message from ban-user {message.from_user.id}")


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message: telebot.types.Message):
    try:
        if message.chat.id == int(CHAT):
            if message.reply_to_message.forward_from is None:
                bot.send_sticker(hidden_forward.get_id(message), message.sticker.file_id)
            else:
                hidden_forward.delete_data(message)
                bot.send_sticker(message.reply_to_message.forward_from.id, message.sticker.file_id)
            logger.info(f"Sticker handler. In CHAT. Info: {message}")
        else:
            send_to_chat(hidden_forward, bot, message, success_mess)
            logger.info(f"Sticker handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.error(f"Exception in sticker handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['photo'])
def images_handler(message: telebot.types.Message):
    try:
        if message.chat.id == int(CHAT):
            if message.reply_to_message.forward_from is None:
                bot.send_photo(hidden_forward.get_id(message), message.photo[-1].file_id)
            else:
                hidden_forward.delete_data(message)
                bot.send_photo(message.reply_to_message.forward_from.id, message.photo[-1].file_id)
            logger.info(f"Photo handler. In CHAT. Info: {message}")
        else:
            send_to_chat(hidden_forward, bot, message, success_mess)
            logger.info(f"Image handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.error(f"Exception in image handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['document'])
def file_handler(message: telebot.types.Message):
    try:
        if message.chat.id == int(CHAT):
            if message.reply_to_message.forward_from is None:
                bot.send_document(hidden_forward.get_id(message), message.document.file_id)
            else:
                hidden_forward.delete_data(message)
                bot.send_document(message.reply_to_message.forward_from.id, message.document.file_id)
            logger.info(f"Document handler. In CHAT. Info: {message}")
        else:
            send_to_chat(hidden_forward, bot, message, success_mess)
            logger.info(f"File handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.error(f"Exception in file handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['audio'])
def audio_handler(message: telebot.types.Message):
    # Have to update the handler
    try:
        if message.chat.id == int(CHAT):
            if message.reply_to_message.forward_from is None:
                bot.send_audio(hidden_forward.get_id(message), message.audio.file_id)
            else:
                hidden_forward.delete_data(message)
                bot.send_audio(message.reply_to_message.forward_from.id, message.audio.file_id)
            logger.info(f"Audio handler. In CHAT. Info: {message}")
        else:
            hidden_forward.add_key(message)
            bot.send_audio(CHAT, message.audio.file_id,
                           caption=info_mess.format(message.from_user.first_name, message.from_user.username),
                           reply_to_message_id=message.from_user.id)
            bot.send_message(message.from_user.id, other_mess)
            bot.send_message(CHAT, message.from_user.id)
            logger.info(f"Audio handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.error(f"Exception in audio handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['voice'])
def voice_handler(message: telebot.types.Message):
    try:
        if message.chat.id == int(CHAT):
            if message.reply_to_message.forward_from is None:
                bot.send_voice(hidden_forward.get_id(message), message.voice.file_id)
            else:
                hidden_forward.delete_data(message)
                bot.send_voice(message.reply_to_message.forward_from.id, message.voice.file_id)
            logger.info(f"Voice handler. In CHAT. Info: {message}")
        else:
            send_to_chat(hidden_forward, bot, message, success_mess)
            logger.info(f"Voice handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.error(f"Exception in voice handler. Info: {error.with_traceback(None)}")


@bot.message_handler(content_types=['text'])
def text_handler(message: telebot.types.Message):
    try:
        if message.chat.id == int(CHAT):
            if message.reply_to_message.forward_from is None:
                bot.send_message(hidden_forward.get_id(message), message.text)
            else:
                hidden_forward.delete_data(message)
                bot.send_message(message.reply_to_message.forward_from.id, message.text)
            logger.info(f"Text handler. In CHAT. Info: {message}")
        else:
            send_to_chat(hidden_forward, bot, message, success_mess)
            logger.info(f"Text handler. Message from a user. Info: {message}")
    except Exception as error:
        logger.error(f"Exception in text handler. Info: {error.with_traceback(None)}")


@bot.message_handler(func=lambda message: True)
def other_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, other_mess)
    logger.info(f"Other handler. Message from a user. Info: {message}")


def create_bot_instance(logging_enable=True, logging_level='DEBUG'):
    if logging_enable:
        telebot.logger.setLevel(logging.getLevelName(logging_level))
    return bot
