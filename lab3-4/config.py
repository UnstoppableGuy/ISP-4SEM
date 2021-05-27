from enum import Enum
import os


class Config(object):
    DEBUG_MODE = True
    API_TOKEN = os.getenv('API_TOKEN ')
    WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
    WEBHOOK_PORT = os.getenv('WEBHOOK_PORT')
    WEBHOOK_LISTEN = '0.0.0.0'
    WEBHOOK_SSL_CERT = os.getenv('WEBHOOK_SSL_CERT')
    WEBHOOK_SSL_PRIVATE_KEY = os.getenv('WEBHOOK_SSL_PRIVATE_KEY')
    ROOT_USER = {'login': 'root', 'password': 'sdfsdfgEG34'}

    DB_CONFIG = {'host': 'localhost', 'port': 28015, }
    DB_NAME = {'db_bot': 'db_bot', 'db_api': 'data'}
    TAB_BOT = {'data': 'data', 'log': 'log', 'root': 'root'}

    USER_PERMISSION = {}

    ID = 'id'
    PAS = 'password'
    LOGIN = 'login'
    CHT = 'ch_date'
    UNAME = 'name'
    GENDER = 'gender'
    PHONE = 'phone'
    EMAIL = 'email'
    DATA_REG = 'reg_date'

    NAME_FIELD = {'id': 'ID', 'login': 'Логин', 'password': 'Пароль', 'reg_date': 'Дата регистрации',
                  'ch_date': 'Дата изменения', 'name': 'Ф.И.О', 'gender': 'Пол', 'phone': 'Номер телефона',
                  'email': 'Эл.почта'}

    USER_DATA = 'Данные пользователя'
    CREATE_USER = 'Создание'
    EDIT_PROFILE = 'Редактирование'
    PASSWORD_RECOVER = 'Восстановление'
    SETTING = 'Настройка'

    MAIN_MENU = 'Главное меню'
    CREATE_DBASE = 'Создать БД'
    DELETE_DBASE = 'Удалить БД'
    CREATE_DB_TAB = 'Создать таблицы'
    LIST_TABLES = 'Список таблиц'
    CREATE_SU_USER = 'Создать админа'
    CHANGE_PASSWORD_SU = 'Изменить пароль админа'
    NAME_EDIT = 'Ф.И.О'
    PASSWORD_EDIT = 'Пароль'
    PHONE_EDIT = 'Телефон'
    EMAIL_EDIT = 'Адрес эл.почты'
    GENDER_EDIT = 'Половая принадлежность'
    DELETE_PROF = 'Удалить'

    SELECT_MENU = 'Выберите пункт меню: '
    NEW_USER = 'Login нового пользователя:'
    NEW_PASSWORD = 'Passwd нового пользователя:'
    NEW_CREATE = 'Поздравляю, новый пользователь создан'
    LOGIN_EXISTS = 'Извините, Login существует\nВведите новый Login:'
    LOGIN_ = 'Login:'
    LOGIN_ERR = 'Ошибка!\nLogin не существует\nВведите Login:'
    LOGIN_NO_VALID = 'Ошибка!\nLogin короткий,\nили содержит не допустимые символы'
    USER_GENDER = 'Укажите ваш пол'
    PASSWORD = 'Введите пароль:'
    PASSWORD_NEW = 'Введите новый пароль'
    PASSWORD_CHANGED = 'Пароль админа изменен'
    PASSWORD_OK = 'Поздравляю, вы ввели верный Login и Passwd'
    PASSWORD_ERROR = 'Ошибка, Passwd не верный. Введите Passwd:'
    PASSWORD_USER_EDIT = 'Пароль изменен'
    PASSWORD_EXPLAIN = """Пароль считается надежным, если:
• длина 8 или больше символов
• включает 1 или более цифру
• имеет 1 или более специальный символ
• имеет 1 или более символ в верхнем регистре
• имеет 1 или более символ в нижнем регистре"""
    PASSWORD_SIMPLE = 'Пароль простой\nВведите более сложный пароль'
    USER_PHONE = 'Введите номер телефона:'
    PHONE_EDT = 'Номер телефона изменен'
    PHONE_ERR = 'Извините, вы ввели номер телефона в неверном формате'
    PHONE_NO_USER = 'Извините, указанный вами\nномер телефона не соответствует\nимеющемуся в БД'
    USER_EMAIL = 'Введите адрес эл. почты: \nНапример: \n mail@mail.ru'
    EMAIL_EDT = 'Адрес электронной почты изменен'
    EMAIL_ERR = 'Извините, вы ввели адрес эл. почты в неверном формате'
    EMAIL_NO_USER = 'Извините, указаный вами\nадрес эл. почты не соответствует\nимеющемуся в БД'
    UNAME_EDIT = 'Укажите пожалуйста, вашу Фамилию, Имя и Отчество\nОдной строкой, через пробел'
    UNAME_SAVE = 'Ваша Фамилия, Имя и Отчество\nсохранены в Базе данных'
    GENDER_SAVE = 'Данные о вашей половой принадлежности\nсохранены в Базе данных'
    LOGIN_SUPERUSER = 'Введите Login админа'
    PASSWORD_SUPERUSER = 'Введите пароль админа'
    DEL_CONFIRM = 'Вы действительно желаете\nудалить вашу учетную запись?\n• Да\n• Нет'
    DEL_COMPLETE = 'Удаление вашей\nучетной записи выполнено'
    NOT_DELETED = 'Отмена уделения'
    SUPERUSER = 'Создать админа'
    SU_CREATE = 'Админ создан'
    SU_CHANGE = 'Пароль админа изменен'
    DB_NO_CREATE = 'БД не создана'
    DB_OK = 'БД успешно создана'
    DB_DEL_OK = 'БД успешно удалена'
    DB_NO_DELETE = 'БД не удалена'
    DELETE_DB = 'Для удаления БД введите: Удалить БД'
    TAB_OK = 'Таблицы созданы'
    FULL_SET = 'Поздравляю, вы выполнили основные настройки приложения.'
    NO_ACCESS = 'У вас нет прав: '
    GUIDE_RECOVERY = 'Для восстановления пароля\nследуйте подсказкам гида'


class Status(Enum):
    START = '0'
    LOGIN_ROOT = '1'
    LOGIN_NEW = '11'
    LOGIN_USER = '100'
    LOGIN_RECOVER = '111'
    PASSWORD_ROOT = '2'
    PASSWORD_NEW = '22'
    PASSWORD_USER = '200'
    PASSWORD_EDIT = '220'
    PASSWORD_RECOVER = '222'
    EMAIL = '3'
    EMAIL_EDIT = '300'
    EMAIL_RECOVER = '30'
    PHONE = '4'
    PHONE_EDIT = '400'
    PHONE_RECOVER = '40'
    NAME = '5'
    GENDER = '6'
    CHECKED = '7'
    SUPERUSER = '8'
    SUPER_PASS = '9'
    CHANGE_SU = '10'
    EDIT = '50'
    DELETE = '500'
