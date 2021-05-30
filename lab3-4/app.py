import aiogram
from aiogram import Bot, Dispatcher
from flask import Flask, request, abort
from dbworker import UseDB
from hashlib import md5
from datetime import datetime
from config import Config
from config import Status
import logging
from telebot import types
import re
import tg_analytics as tga
app = Flask(__name__)
app.config.from_object(Config)

bot = Bot(app.config['API_TOKEN'])
dp = Dispatcher(bot)
logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename=u'logs.log')
logger = logging.getLogger(__name__)

WEBHOOK_PORT = app.config['WEBHOOK_PORT']
WEBHOOK_LISTEN = app.config['WEBHOOK_LISTEN']
WEBHOOK_URL_BASE = 'https://{}:{}'.format(
    app.config['WEBHOOK_HOST'], app.config['WEBHOOK_PORT'])
WEBHOOK_URL_PATH = '/{}/'.format(app.config['API_TOKEN'])
WEBHOOK_SSL_CERT = app.config['WEBHOOK_SSL_CERT']
WEBHOOK_SSL_PRIVATE_KEY = app.config['WEBHOOK_SSL_PRIVATE_KEY']

DB_CONF = app.config['DB_CONFIG']
DB_BOT = app.config['DB_NAME']['db_bot']
TAB_DATA = app.config['TAB_BOT']['data']
TAB_LOG = app.config['TAB_BOT']['log']
TAB_ROOT = app.config['TAB_BOT']['root']
ROOT_LOGIN = app.config['ROOT_USER']['login']
ROOT_PASSWORD = app.config['ROOT_USER']['password']
USER = app.config['USER_PERMISSION']
DB = UseDB(DB_CONF)
ST = Status
NAME = app.config['NAME_FIELD']
ID, PAS, LOGIN, CHT, GENDER, PHONE, EMAIL, DATA_REG, UNAME = \
    app.config['ID'], app.config['PAS'], \
    app.config['LOGIN'], app.config['CHT'], \
    app.config['GENDER'], app.config['PHONE'], \
    app.config['EMAIL'], app.config['DATA_REG'], \
    app.config['UNAME']


def save_user_activity():
    def decorator(func):
        @wraps(func)
        def command_func(message, *args, **kwargs):
            tga.statistics(message.chat.id, message.text)
            return func(message, *args, **kwargs)

        return command_func

    return decorator


def save_state(id_bot=None, login=None, pas=None, st=None,
               gender=None, ph=None, em=None, name=None, res=False):
    s = DB.presence_id(DB_BOT, TAB_LOG, ID, str(id_bot))
    dit_json = {CHT: datetime.now().strftime("%Y-%m-%d %X"),
                str(id_bot): st if id_bot else None}
    if login or res:
        dit_json[LOGIN] = login if not res else 'xxxxxxxxx'
    if pas or res:
        dit_json[PAS] = pas if not res else 'xxxxxxxxx'
    if gender or res:
        dit_json[GENDER] = gender if not res else 'xxxxxxxxx'
    if ph or res:
        dit_json[PHONE] = ph if not res else 'xxxxxxxxx'
    if em or res:
        dit_json[EMAIL] = em if not res else 'xxxxxxxxx'
    if name or res:
        dit_json[UNAME] = name if not res else 'xxxxxxxxx'
    if s == 1:
        DB.update_one_user(DB_BOT, TAB_LOG, str(id_bot), dit_json)
    elif s == 0:
        dit_json[ID] = str(id_bot)
        dit_json[DATA_REG] = datetime.now().strftime("%Y-%m-%d %X")
        db = DB.new_record(DB_BOT, TAB_LOG, dit_json)
        if 'the table does not exist' in str(db):
            USER.update(dit_json)

    if app.config['DEBUG_MODE'] and s:
        print(DB.get_user_id(DB_BOT, TAB_LOG, str(id_bot)))


def print_user(db, tab, user_id, msg_id):
    for i in list(DB.get_one_user(db, tab, user_id).items()):
        if i[0] == 'password':
            bot.send_message(msg_id,
                             '{}: {}'.format(NAME[i[0]], '**************'))
        else:
            bot.send_message(msg_id,
                             '{}: {}'.format(NAME[i[0]], i[1]))


def valid_login(login):
    if len(login) >= 4:
        if re.match(r'^[a-z0-9\+_-]', login) is not None:
            return True
    return False


def valid_email(email):
    if len(email) > 7:
        if re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$',
                    email) is not None:
            return True
    return False


def valid_phone(phone):
    if len(phone) > 7:
        if re.match(r'^((9|\+375)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$',
                    phone) is not None:
            return True
    return False


def password_check(password):
    length_error = len(password) < 8
    digit_error = re.search(r"\d", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]',
                             password) is None

    password_ok = not (length_error or digit_error or uppercase_error
                       or lowercase_error or symbol_error)

    return password_ok


def set_password(login: str, password: str) -> str:
    return str(md5(str(password + login).lower().encode('utf-8')).hexdigest())


def verify(id_bot, username=None, password=None):
    if not password and username:
        root_db = DB.get_root_user(DB_BOT, TAB_ROOT, LOGIN)
        if root_db and DB.presence_id(DB_BOT, TAB_ROOT, ID, username) == 1:
            return DB.get_one_user(DB_BOT, TAB_ROOT, username)[ID]
        elif not root_db and username and username == ROOT_LOGIN:
            return ROOT_LOGIN
        else:
            return None
    elif not username and password:
        root_db = DB.get_root_user(DB_BOT, TAB_ROOT, LOGIN)
        if root_db:
            login = DB.get_user_id(DB_BOT, TAB_LOG, id_bot)[LOGIN]
            pas = set_password(login, password)
        else:
            pas = set_password(ROOT_LOGIN, password)
        if root_db and DB.presence_id(DB_BOT, TAB_ROOT, PAS, pas) == 1:
            return DB.get_one_user(DB_BOT, TAB_ROOT, login)[PAS]
        elif not root_db and password and pas == ROOT_PASSWORD:
            return ROOT_PASSWORD
        else:
            return None
    else:
        return None


@dp.message_handler(commands=['start'])
async def start_bot(message):
    await bot.send_sticker(message.chat.id, sticker='CAACAgIAAxkBAAECTkZgn54R122JUR1uILtdhjwUWbw-CQACFAEAAvcCyA9r'
                                                    '-vWtjqTjLB8E')
    save_state(id_bot=str(message.chat.id), st=ST.START.value, res=True)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['USER_DATA'])
    user_markup.row(app.config['CREATE_USER'], app.config['PASSWORD_RECOVERY'])
    await bot.send_message(message.from_user.id,
                           app.config['SELECT_MENU'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: app.config['MAIN_MENU'] == message.text, content_types=['text'])
async def main_menu(message):
    save_state(id_bot=str(message.chat.id), st=ST.START.value, res=True)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['USER_DATA'])
    user_markup.row(app.config['CREATE_USER'], app.config['PASSWORD_RECOVERY'])

    await bot.send_message(message.from_user.id, app.config['SELECT_MENU'],
                           reply_markup=user_markup)


@dp.message_handler(func=lambda message: app.config['USER_DATA'] == message.text, content_types=['text'])
async def user_data(message):
    save_state(id_bot=str(message.chat.id), st=ST.LOGIN_USER.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    await bot.send_message(message.from_user.id,
                           app.config['LOGIN'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.LOGIN_USER.value)
async def get_login_user(message):
    if DB.presence_id(DB_BOT, TAB_DATA, ID, str(message.text)):
        save_state(id_bot=str(message.chat.id), login=message.text.lower(),
                   st=ST.PASSWORD_USER.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        await bot.send_message(message.from_user.id,
                               app.config['PASSWORD'], reply_markup=user_markup)
    else:
        await bot.send_message(message.from_user.id, app.config['LOGIN_ERR'])
        return


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.PASSWORD_USER.value)
async def get_password_user(message):
    login = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN]
    pas = set_password(login, message.text)
    if DB.get_user_id(DB_BOT, TAB_DATA, login)[PAS] == pas:
        save_state(id_bot=str(message.chat.id), login=login, pas=pas,
                   st=ST.EDIT.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

        print_user(DB_BOT, TAB_DATA, login, message.chat.id)
        await bot.send_message(message.from_user.id,
                               app.config['SELECT_MENU'], reply_markup=user_markup)
    else:
        await bot.send_message(message.from_user.id, app.config['PASSWORD_ERROR'])
        return


@dp.message_handler(func=lambda message: app.config['PASSWORD_EDIT'] == message.text, content_types=['text'])
async def edit_password_user(message):
    save_state(id_bot=str(message.chat.id), st=ST.PASSWORD_EDIT.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

    await bot.send_message(message.from_user.id, app.config['PASSWORD_EXPLAIN'])
    await bot.send_message(message.from_user.id,
                           app.config['PASSWORD'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.PASSWORD_EDIT.value)
async def save_pass(message):
    if password_check(message.text):
        js = {LOGIN: DB.get_user_id(
            DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN]}
        js[PAS] = set_password(js[LOGIN], message.text)
        js[CHT] = datetime.now().strftime("%Y-%m-%d %X")
        DB.update_one_user(DB_BOT, TAB_DATA, js[LOGIN], js)
        save_state(id_bot=str(message.chat.id), pas=js[PAS], st=ST.EDIT.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['EDIT_PROFILE'])

        await bot.send_message(message.from_user.id,
                               app.config['PASSWORD_USER_EDIT'], reply_markup=user_markup)
        print_user(DB_BOT, TAB_DATA, js[LOGIN], message.chat.id)
    else:
        await bot.send_message(message.from_user.id, app.config['PASSWORD_SIMPLE'])
        await bot.send_message(message.from_user.id, app.config['PASSWORD_EXPLAIN'])
        await bot.send_message(message.from_user.id, app.config['PASSWORD'])
        return


@dp.message_handler(func=lambda message: app.config['PHONE_EDIT'] == message.text, content_types=['text'])
async def edit_phone(message):
    save_state(id_bot=str(message.chat.id), st=ST.PHONE_EDIT.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

    await bot.send_message(message.from_user.id,
                           app.config['USER_PHONE'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.PHONE_EDIT.value)
async def save_phone(message):
    if valid_phone(message.text):
        js = {LOGIN: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN], PHONE: message.text,
              CHT: datetime.now().strftime("%Y-%m-%d %X")}
        DB.update_one_user(DB_BOT, TAB_DATA, js[LOGIN], js)
        save_state(id_bot=str(message.chat.id),
                   ph=message.text, st=ST.EDIT.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

        await bot.send_message(message.from_user.id,
                               app.config['PHONE_EDT'], reply_markup=user_markup)
        print_user(DB_BOT, TAB_DATA, js[LOGIN], message.chat.id)
    else:
        await bot.send_message(message.from_user.id, app.config['PHONE_ERR'])
        await bot.send_message(message.from_user.id, app.config['USER_PHONE'])
        return


@dp.message_handler(func=lambda message: app.config['EMAIL_EDIT'] == message.text, content_types=['text'])
async def edit_email(message):
    save_state(id_bot=str(message.chat.id), st=ST.EMAIL_EDIT.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

    await bot.send_message(message.from_user.id,
                           app.config['USER_EMAIL'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.EMAIL_EDIT.value)
async def save_email(message):
    if valid_email(message.text):
        login = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN]
        js = {LOGIN: login, EMAIL: message.text,
              CHT: datetime.now().strftime("%Y-%m-%d %X")}
        DB.update_one_user(DB_BOT, TAB_DATA, js[LOGIN], js)
        save_state(id_bot=str(message.chat.id),
                   em=message.text, st=ST.EDIT.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

        await bot.send_message(message.from_user.id,
                               app.config['EMAIL_EDIT'], reply_markup=user_markup)
        print_user(DB_BOT, TAB_DATA, login, message.chat.id)
    else:
        await bot.send_message(message.from_user.id, app.config['EMAIL_ERR'])
        await bot.send_message(message.from_user.id, app.config['USER_EMAIL'])
        return


@dp.message_handler(func=lambda message: app.config['GENDER_EDIT'] == message.text, content_types=['text'])
async def edit_gender(message):
    save_state(id_bot=str(message.chat.id), st=ST.GENDER.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

    await bot.send_message(message.from_user.id,
                           app.config['USER_GENDER'], reply_markup=user_markup)


@dp.message_handler(
    func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] == ST.GENDER.value)
async def save_gender(message):
    js = {LOGIN: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN], GENDER: message.text,
          CHT: datetime.now().strftime("%Y-%m-%d %X")}
    DB.update_one_user(DB_BOT, TAB_DATA, js[LOGIN], js)
    save_state(id_bot=str(message.chat.id),
               gender=message.text, st=ST.EDIT.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

    await bot.send_message(message.from_user.id,
                           app.config['GENDER_SAVE'], reply_markup=user_markup)
    print_user(DB_BOT, TAB_DATA, js[LOGIN], message.chat.id)


@dp.message_handler(func=lambda message: app.config['NAME_EDIT'] == message.text, content_types=['text'])
async def edit_name(message):
    save_state(id_bot=str(message.chat.id), st=ST.NAME.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

    await bot.send_message(message.from_user.id,
                           app.config['UNAME_EDIT'], reply_markup=user_markup)


@dp.message_handler(
    func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] == ST.NAME.value)
async def save_name(message):
    js = {LOGIN: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN], UNAME: message.text,
          CHT: datetime.now().strftime("%Y-%m-%d %X")}
    DB.update_one_user(DB_BOT, TAB_DATA, js[LOGIN], js)
    save_state(id_bot=str(message.chat.id),
               name=message.text, st=ST.EDIT.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'], app.config['EDIT_PROFILE'])

    await bot.send_message(message.from_user.id,
                           app.config['UNAME_SAVE'], reply_markup=user_markup)
    print_user(DB_BOT, TAB_DATA, js[LOGIN], message.chat.id)


@dp.message_handler(func=lambda message: app.config['DELETE_PROF'] == message.text, content_types=['text'])
async def delete_request(message):
    save_state(id_bot=str(message.chat.id), st=ST.DELETE.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    await bot.send_message(message.from_user.id,
                           app.config['DEL_CONFIRM'], reply_markup=user_markup)


@dp.message_handler(
    func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] == ST.DELETE.value)
async def delete_confirm(message):
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    if message.text.lower() == 'да' or message.text.lower() == 'yes':
        login = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN]
        DB.delete_one_user(DB_BOT, TAB_DATA, login)
        save_state(id_bot=str(message.chat.id), res=True, st=ST.START.value)
        await bot.send_message(message.from_user.id,
                               app.config['DEL_COMPLETE'], reply_markup=user_markup)
    else:
        save_state(id_bot=str(message.chat.id), st=ST.START.value)
        await bot.send_message(message.from_user.id,
                               app.config['NOT_DELETED'], reply_markup=user_markup)


@dp.message_handler(
    func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] == ST.EDIT.value)
async def edit_profile(message):
    user_markup = types.ReplyKeyboardMarkup(True, False)
    save_state(id_bot=str(message.chat.id), st=ST.EDIT.value)
    user_markup.row(app.config['MAIN_MENU'], app.config['NAME_EDIT'])
    user_markup.row(app.config['PHONE_EDIT'], app.config['EMAIL_EDIT'])
    user_markup.row(app.config['PASSWORD_CHANGED'], app.config['GENDER_EDIT'])
    user_markup.row(app.config['DELETE_PROF'], app.config['FEEDBACK'])
    await bot.send_message(message.from_user.id,
                           app.config['SELECT_MENU'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: app.config['CREATE_USER'] == message.text, content_types=['text'])
async def new_user(message):
    save_state(id_bot=str(message.chat.id), st=ST.LOGIN_NEW.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    await bot.send_message(message.from_user.id,
                           app.config['NEW_USER'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.LOGIN_NEW.value)
async def new_login(message):
    if not DB.presence_id(DB_BOT, TAB_DATA, ID, str(message.text.lower())) \
            and valid_login(str(message.text.lower())):
        save_state(id_bot=str(message.chat.id), login=message.text.lower(),
                   st=ST.PASSWORD_NEW.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        await bot.send_message(message.from_user.id,
                               app.config['NEW_PASSWORD'])
        await bot.send_message(message.from_user.id, app.config['PASSWORD_EXPLAIN'],
                               reply_markup=user_markup)
    else:
        if not valid_login(str(message.text.lower())):
            await bot.send_message(message.chat.id, app.config['LOGIN_NO_VALID'])
        else:
            await bot.send_message(message.chat.id, app.config['LOGIN_EXISTS'])
        return


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.PASSWORD_NEW.value)
async def new_password(message):
    if password_check(message.text):
        usr = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))
        pas = set_password(usr[LOGIN], message.text)
        save_state(id_bot=str(message.chat.id), pas=pas, st=ST.EMAIL.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        await bot.send_message(message.from_user.id,
                               app.config['USER_EMAIL'], reply_markup=user_markup)
    else:
        await bot.send_message(message.from_user.id, app.config['PASSWORD_SIMPLE'])
        await bot.send_message(message.from_user.id, app.config['PASSWORD_EXPLAIN'])
        await bot.send_message(message.from_user.id, app.config['PASSWORD'])
        return


@dp.message_handler(
    func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] == ST.EMAIL.value)
async def new_email(message):
    if valid_email(message.text):
        save_state(id_bot=str(message.chat.id),
                   em=message.text, st=ST.PHONE.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        await bot.send_message(message.from_user.id,
                               app.config['USER_PHONE'], reply_markup=user_markup)
    else:
        await bot.send_message(message.chat.id, app.config['EMAIL_ERR'])
        await bot.send_message(message.chat.id, app.config['USER_EMAIL'])
        return


@dp.message_handler(
    func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] == ST.PHONE.value)
async def create_user(message):
    if valid_phone(message.text):
        save_state(id_bot=str(message.chat.id),
                   ph=message.text, st=ST.PHONE.value)
        usr = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))
        new_usr = {ID: usr[LOGIN], PAS: usr[PAS], LOGIN: usr[LOGIN], CHT: datetime.now().strftime("%Y-%m-%d %X"),
                   PHONE: usr[PHONE], EMAIL: usr[EMAIL], DATA_REG: datetime.now().strftime("%Y-%m-%d %X")}
        DB.new_record(DB_BOT, TAB_DATA, new_usr)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        print_user(DB_BOT, TAB_DATA, usr[LOGIN], message.chat.id)
        await bot.send_message(message.from_user.id,
                               app.config['NEW_CREATE'], reply_markup=user_markup)
    else:
        await bot.send_message(message.chat.id, app.config['PHONE_ERR'])
        await bot.send_message(message.chat.id, app.config['USER_PHONE'])
        return


@dp.message_handler(func=lambda message: app.config['PASSWORD_RECOVERY'] == message.text, content_types=['text'])
async def recover_get_user(message):
    save_state(id_bot=str(message.chat.id),
               st=ST.LOGIN_RECOVER.value, res=True)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    await bot.send_message(message.chat.id, app.config['GUIDE_RECOVERY'])
    await bot.send_message(message.from_user.id,
                           app.config['LOGIN'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.LOGIN_RECOVER.value)
async def recover_get_email(message):
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    if DB.presence_id(DB_BOT, TAB_DATA, ID, str(message.text.lower())) \
            and valid_login(str(message.text.lower())):
        save_state(id_bot=str(message.chat.id), login=message.text.lower(),
                   st=ST.EMAIL_RECOVER.value)
        await bot.send_message(message.from_user.id, app.config['USER_EMAIL'],
                               reply_markup=user_markup)
    else:
        if not valid_login(str(message.text.lower())):
            await bot.send_message(message.chat.id, app.config['LOGIN_NO_VALID'],
                                   reply_markup=user_markup)
        else:
            await bot.send_message(message.chat.id, app.config['LOGIN_ERR'],
                                   reply_markup=user_markup)
        return


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.EMAIL_RECOVER.value)
async def recover_get_phone(message):
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    if valid_email(str(message.text)):
        usr = DB.get_one_user(DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN]
        print(usr)
        email = DB.get_one_user(DB_BOT, TAB_DATA, usr)[EMAIL]
        print(email)
        if email == str(message.text):
            save_state(id_bot=str(message.chat.id), em=message.text,
                       st=ST.PHONE_RECOVER.value)
            await bot.send_message(message.from_user.id, app.config['USER_PHONE'],
                                   reply_markup=user_markup)
        else:
            await bot.send_message(message.chat.id, app.config['EMAIL_NO_USER'])
            await bot.send_message(message.from_user.id, app.config['USER_EMAIL'],
                                   reply_markup=user_markup)
            return
    else:
        await bot.send_message(message.chat.id, app.config['EMAIL_ERR'])
        await bot.send_message(message.from_user.id, app.config['USER_EMAIL'],
                               reply_markup=user_markup)
        return


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.PHONE_RECOVER.value)
async def recover_get_pass(message):
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    if valid_phone(str(message.text)):
        usr = DB.get_one_user(DB_BOT, TAB_LOG, str(message.chat.id))[LOGIN]
        print(usr)
        phone = DB.get_one_user(DB_BOT, TAB_DATA, usr)[PHONE]
        print(phone)
        if phone == str(message.text):
            save_state(id_bot=str(message.chat.id), ph=message.text,
                       st=ST.PASSWORD_RECOVER.value)
            await bot.send_message(message.chat.id, app.config['PASSWORD_EXPLAIN'])
            await bot.send_message(message.from_user.id, app.config['PASSWORD_NEW'],
                                   reply_markup=user_markup)
        else:
            await bot.send_message(message.chat.id, app.config['PHONE_NO_USER'])
            await bot.send_message(message.from_user.id, app.config['USER_PHONE'],
                                   reply_markup=user_markup)
            return
    else:
        await bot.send_message(message.chat.id, app.config['PHONE_ERR'])
        await bot.send_message(message.from_user.id, app.config['USER_PHONE'],
                               reply_markup=user_markup)
        return


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.PASSWORD_RECOVER.value)
async def recover_password_user(message):
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    if password_check(str(message.text)):
        db = DB.get_one_user(DB_BOT, TAB_LOG, str(message.chat.id))
        passw = {PAS: set_password(db[LOGIN], str(
            message.text)), CHT: datetime.now().strftime("%Y-%m-%d %X")}
        DB.update_one_user(DB_BOT, TAB_DATA, db[LOGIN], passw)
        print_user(DB_BOT, TAB_DATA, db[LOGIN], message.chat.id)
        save_state(id_bot=str(message.chat.id), pas=passw[PAS],
                   st=ST.START.value)
        await bot.send_message(message.from_user.id, app.config['PASSWORD_USER_EDIT'],
                               reply_markup=user_markup)
    else:
        await bot.send_message(message.chat.id, app.config['PASSWORD_EXPLAIN'])
        await bot.send_message(message.from_user.id, app.config['PASSWORD_NEW'],
                               reply_markup=user_markup)
        return


@dp.message_handler(commands=['setting'])
async def setting_app(message):
    save_state(id_bot=str(message.chat.id), st=ST.LOGIN_ROOT.value, res=True)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    await bot.send_message(message.from_user.id,
                           app.config['LOGIN'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.LOGIN_ROOT.value)
async def user_entering_name(message):
    if verify(str(message.chat.id), username=message.text) == message.text:
        save_state(id_bot=str(message.chat.id),
                   login=message.text, st=ST.PASSWORD_ROOT.value)
        await bot.send_message(message.chat.id, app.config['PASSWORD'])
    else:
        await bot.send_message(message.chat.id, app.config['LOGIN_ERR'])
        return


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.PASSWORD_ROOT.value)
async def user_entering_password(message):
    usr = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))
    if verify(str(message.chat.id), password=message.text) == \
            set_password(usr[LOGIN].lower(), message.text):
        passw = set_password(usr[LOGIN].lower(), message.text)
        save_state(id_bot=str(message.chat.id), pas=passw, st=ST.CHECKED.value)
        await bot.send_message(message.chat.id, app.config['PASSWORD_OK'])
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])
        if DB_BOT not in DB.db_init(DB_BOT).keys():
            user_markup.row(app.config['CREATE_DBASE'])

        else:
            m = 'not found'
            if m in str(DB.tab_all(DB_BOT)):
                user_markup.row(app.config['CREATE_DB_TAB'],
                                app.config['DELETE_DBASE'])
            else:
                user_markup.row(app.config['LIST_TABLES'])
                if not DB.get_root_user(DB_BOT, TAB_ROOT, LOGIN):
                    user_markup.row(app.config['DELETE_DBASE'],
                                    app.config['CREATE_SU_USER'])
                else:
                    user_markup.row(app.config['DELETE_DBASE'],
                                    app.config['CHANGE_PASSWORD_SU'])

        await bot.send_message(message.from_user.id,
                               app.config['SELECT_MENU'], reply_markup=user_markup)
    else:
        await bot.send_message(message.chat.id, app.config['PASSWORD_ERROR'])
        return


@dp.message_handler(func=lambda message: app.config['CREATE_DBASE'] == message.text, content_types=['text'])
async def creating_database(message):
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])
    if DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] \
            == ST.CHECKED.value:
        save_state(id_bot=str(message.chat.id), st=ST.CHECKED.value)
        DB.db_init(DB_BOT)
        if DB_BOT not in DB.db_init(DB_BOT).keys():
            user_markup.row(app.config['CREATE_DBASE'])

            await bot.send_message(message.from_user.id,
                                   app.config['DB_NO_CREATE'], reply_markup=user_markup)
        else:
            user_markup.row(app.config['CREATE_DB_TAB'])

            await bot.send_message(message.from_user.id,
                                   app.config['DB_OK'], reply_markup=user_markup)
        await bot.send_message(message.from_user.id,
                               app.config['SELECT_MENU'], reply_markup=user_markup)
    else:

        await bot.send_message(message.chat.id, app.config['NO_ACCESS'] +
                               app.config['CREATE_DBASE'])


@dp.message_handler(func=lambda message: app.config['DELETE_DBASE'] == message.text, content_types=['text'])
async def deleting_database(message):
    save_state(id_bot=str(message.chat.id), st=ST.CHECKED.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])
    if DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] \
            == ST.CHECKED.value:
        if DB_BOT not in DB.db_delete(DB_BOT).keys():
            save_state(id_bot=str(message.chat.id), st=ST.CHECKED.value)
            user_markup.row(app.config['CREATE_DBASE'])

            await bot.send_message(message.from_user.id,
                                   app.config['DB_DEL_OK'], reply_markup=user_markup)
            await bot.send_message(message.from_user.id,
                                   app.config['SELECT_MENU'], reply_markup=user_markup)
        else:
            save_state(id_bot=str(message.chat.id), st=ST.CHECKED.value)
            user_markup.row(app.config['DELETE_DBASE'])

            await bot.send_message(message.from_user.id,
                                   app.config['DB_NO_DELETE'], reply_markup=user_markup)
            await bot.send_message(message.from_user.id,
                                   app.config['SELECT_MENU'], reply_markup=user_markup)
    else:
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        await bot.send_message(message.chat.id, app.config['NO_ACCESS']
                               + app.config['CREATE_DBASE'])


@dp.message_handler(func=lambda message: app.config['CREATE_DB_TAB'] == message.text, content_types=['text'])
async def creating_tables(message, user_markup=None):
    if DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] \
            == ST.CHECKED.value:
        save_state(id_bot=str(message.chat.id), st=ST.CHECKED.value)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])
        name = list(app.config['TAB_BOT'].values())
        t = 0
        a = 0
        for n in range(len(name)):
            m = DB.tab_creat(DB_BOT, name[n])
            ok = 'tables_created'
            if ok in list(m.keys()):
                t += 1
                await bot.send_message(message.chat.id,
                                       'Таблица {} {} создана'.format(t, name[n]))
            else:
                a += 1
                await bot.send_message(message.chat.id,
                                       'Таблица {} {} уже существует'.format(a, name[n]))
        if a:
            user_markup.row(app.config['LIST_TABLES'])

            await bot.send_message(message.from_user.id,
                                   app.config['SELECT_MENU'], reply_markup=user_markup)
        elif t:
            save_state(id_bot=str(message.chat.id), st=ST.SUPERUSER.value)

            await bot.send_message(message.from_user.id, app.config['TAB_OK'])
            await bot.send_message(message.from_user.id, app.config['SUPERUSER'])
            await bot.send_message(message.from_user.id,
                                   app.config['LOGIN_SUPERUSER'], reply_markup=user_markup)
    else:

        await bot.send_message(message.chat.id, app.config['NO_ACCESS']
                               + app.config['CREATE_DB_TAB'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: app.config['LIST_TABLES'] == message.text, content_types=['text'])
async def list_tables(message):
    if DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[str(message.chat.id)] \
            == ST.CHECKED.value:
        for m in DB.tab_all(DB_BOT):
            await bot.send_message(message.from_user.id,
                                   'Таблица {} в БД {}'.format(m, DB_BOT))
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        await bot.send_message(message.from_user.id,
                               app.config['SELECT_MENU'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: app.config['CREATE_SU_USER'] == message.text, content_types=['text'])
async def get_login_adm(message):
    save_state(id_bot=str(message.chat.id), st=ST.SUPERUSER.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    await bot.send_message(message.from_user.id, app.config['SUPERUSER'])
    await bot.send_message(message.from_user.id,
                           app.config['LOGIN_SUPERUSER'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.SUPERUSER.value)
async def get_password_adm(message):
    if valid_login(str(message.text.lower())):
        save_state(id_bot=str(message.chat.id),
                   login=message.text, st=ST.SUPER_PASS.value)
        await bot.send_message(message.from_user.id, app.config['PASSWORD_SUPERUSER'])
    else:
        await bot.send_message(message.chat.id, app.config['LOGIN_NO_VALID'])


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.SUPER_PASS.value)
async def set_password_superuser(message):
    if password_check(message.text):
        usr = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))
        pas = set_password(usr[LOGIN], message.text)
        save_state(id_bot=str(message.chat.id),
                   pas=pas, st=ST.SUPER_PASS.value)
        usr = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))
        adm = {}
        adm[ID] = usr[LOGIN].lower()
        adm[LOGIN] = adm[ID]
        adm[PAS] = usr[PAS]
        adm[DATA_REG] = datetime.now().strftime("%Y-%m-%d %X")
        adm[CHT] = adm[DATA_REG]
        DB.new_record(DB_BOT, TAB_ROOT, adm)
        print_user(DB_BOT, TAB_ROOT, adm[LOGIN], message.chat.id)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        await bot.send_message(message.from_user.id, app.config['SU_CREATE'])
        await bot.send_message(message.chat.id, app.config['SELECT_MENU'],
                               reply_markup=user_markup)
    else:
        await bot.send_message(message.from_user.id, app.config['PASSWORD_SIMPLE'])
        await bot.send_message(message.from_user.id, app.config['PASSWORD_EXPLAIN'])
        await bot.send_message(message.from_user.id,
                               app.config['PASSWORD_SUPERUSER'])
        return


@dp.message_handler(func=lambda message: app.config['CHANGE_PASSWORD_SU'] == message.text, content_types=['text'])
async def edit_password_adm(message):
    save_state(id_bot=str(message.chat.id), st=ST.CHANGE_SU.value)
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.row(app.config['MAIN_MENU'])

    await bot.send_message(message.from_user.id, app.config['CHANGE_PASSWORD_SU'])
    await bot.send_message(message.from_user.id,
                           app.config['PASSWORD_SUPERUSER'], reply_markup=user_markup)


@dp.message_handler(func=lambda message: DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))[
    str(message.chat.id)] == ST.CHANGE_SU.value)
async def update_password_superuser(message):
    if password_check(message.text):
        usr = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))
        pas = set_password(usr[LOGIN], message.text)
        save_state(id_bot=str(message.chat.id), pas=pas, st=ST.CHANGE_SU.value)
        usr = DB.get_user_id(DB_BOT, TAB_LOG, str(message.chat.id))
        adm = {PAS: usr[PAS], CHT: datetime.now().strftime("%Y-%m-%d %X")}
        DB.update_one_user(DB_BOT, TAB_ROOT, usr[LOGIN].lower(), adm)
        print_user(DB_BOT, TAB_ROOT, usr[LOGIN], message.chat.id)
        user_markup = types.ReplyKeyboardMarkup(True, False)
        user_markup.row(app.config['MAIN_MENU'])

        await bot.send_message(message.from_user.id, app.config['SU_CHANGE'])
        await bot.send_message(message.chat.id, app.config['SELECT_MENU'],
                               reply_markup=user_markup)
    else:
        await bot.send_message(message.from_user.id, app.config['PASSWORD_SIMPLE'])
        await bot.send_message(message.from_user.id, app.config['PASSWORD_EXPLAIN'])
        await bot.send_message(message.from_user.id,
                               app.config['PASSWORD_SUPERUSER'])
        return


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = aiogram.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

if __name__ == '__main__':
    app.run(host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIVATE_KEY),
            debug=True)
