import logging
import os
import sys
import time
import spamwatch
import telegram.ext as tg
from telethon import TelegramClient
from telethon.sessions import MemorySession
from configparser import ConfigParser
from ptbcontrib.postgres_persistence import PostgresPersistence
from logging.config import fileConfig

StartTime = time.time()

def get_user_list(key):
    # Import here to evade a circular import
    from tg_bot.modules.sql import nation_sql
    royals = nation_sql.get_royals(key)
    return [a.user_id for a in royals]

# enable logging

fileConfig('logging.ini')

log = logging.getLogger('[Enterprise]')
logging.getLogger('ptbcontrib.postgres_persistence.postgrespersistence').setLevel(logging.WARNING)
log.info("[Psycho] Psycho başlatılıyor. The Psycho's Bot")
log.info("[Psycho] Bot hiçbir (t.me/The_Psychos) kanalına bağlıdır.")
log.info("[Psycho] Projeyi Değiştirip Sürdüren Kişi : (t.me/IAMCR4ZY)")

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 7:
    log.error(
        "[Psycho]En az 3.7'lik bir python sürümüne sahip olmalısınız! Birçok özellik buna bağlıdır. Bot ayrılıyor."
    )
    quit(1)

parser = ConfigParser()
parser.read("config.ini")
psyconfig = parser["psyconfig"]

class PsychoINIT:
    def __init__(self, parser):
        self.parser = parser
        self.SYS_ADMIN = self.parser.getint('SYS_ADMIN', 0)
        self.OWNER_ID = self.parser.getint('OWNER_ID')
        self.OWNER_USERNAME = self.parser.get('OWNER_USERNAME', None)
        self.APP_ID = self.parser.getint("APP_ID")
        self.API_HASH = self.parser.get("API_HASH")
        self.WEBHOOK = self.parser.getboolean('WEBHOOK', False)
        self.URL = self.parser.get('URL', None)
        self.CERT_PATH = self.parser.get('CERT_PATH', None)
        self.PORT = self.parser.getint('PORT', None)
        self.INFOPIC = self.parser.getboolean('INFOPIC', False)
        self.DEL_CMDS = self.parser.getboolean("DEL_CMDS", False)
        self.STRICT_GBAN = self.parser.getboolean("STRICT_GBAN", False)
        self.ALLOW_EXCL = self.parser.getboolean("ALLOW_EXCL", False)
        self.CUSTOM_CMD = ['/', '!']
        self.BAN_STICKER = self.parser.get("BAN_STICKER", None)
        self.TOKEN = self.parser.get("TOKEN")
        self.DB_URI = self.parser.get("SQLALCHEMY_DATABASE_URI")
        self.LOAD = self.parser.get("LOAD").split()
        self.LOAD = list(map(str, self.LOAD))
        self.MESSAGE_DUMP = self.parser.getint('MESSAGE_DUMP', None)
        self.GBAN_LOGS = self.parser.getint('GBAN_LOGS', None)
        self.NO_LOAD = self.parser.get("NO_LOAD").split()
        self.NO_LOAD = list(map(str, self.NO_LOAD))
        self.spamwatch_api = self.parser.get('spamwatch_api', None)
        self.CASH_API_KEY = self.parser.get('CASH_API_KEY', None)
        self.TIME_API_KEY = self.parser.get('TIME_API_KEY', None)
        self.WALL_API = self.parser.get('WALL_API', None)
        self.LASTFM_API_KEY = self.parser.get('LASTFM_API_KEY', None)
        self.CF_API_KEY =  self.parser.get("CF_API_KEY", None)
        self.bot_id = 0 #placeholder
        self.bot_name = "The Psycho" #placeholder
        self.bot_username = "ThePsychos_Bot" #placeholder


    def init_sw(self):
        if self.spamwatch_api is None:
            log.warning("Spamİzleyici API anahtarı yok! config.ini kısmını kontrol et.")
            return None
        else:
            try:
                sw = spamwatch.Client(spamwatch_api)
                return sw
            except:
                sw = None
                log.warning("Spamİzleyici'ye bağlanılamadı!")
                return sw


PSnit = PSYCHOINIT(parser=psychoconfig)

SYS_ADMIN = PSnit.SYS_ADMIN
OWNER_ID = PSnit.OWNER_ID
OWNER_USERNAME = PSnit.OWNER_USERNAME
APP_ID = PSnit.APP_ID
API_HASH = PSnit.API_HASH
WEBHOOK = PSnit.WEBHOOK
URL = PSnit.URL
CERT_PATH = PSnit.CERT_PATH
PORT = PSnit.PORT
INFOPIC = PSnit.INFOPIC
DEL_CMDS = PSnit.DEL_CMDS
ALLOW_EXCL = PSnit.ALLOW_EXCL
CUSTOM_CMD = PSnit.CUSTOM_CMD
BAN_STICKER = PSnit.BAN_STICKER
TOKEN = PSnit.TOKEN
DB_URI = PSnit.DB_URI
LOAD = PSnit.LOAD
MESSAGE_DUMP = PSnit.MESSAGE_DUMP
GBAN_LOGS = PSnit.GBAN_LOGS
NO_LOAD = PSnit.NO_LOAD
SUDO_USERS = [OWNER_ID] + get_user_list("sudo kullanıcıları")
DEV_USERS = [OWNER_ID] + get_user_list("devler")
SUPPORT_USERS = get_user_list("destekçiler")
SARDEGNA_USERS = get_user_list("sardegna'lar")
WHITELIST_USERS = get_user_list("beyaz liste")
SPAMMERS = get_user_list("kötü amaçlı kullanıcılar")
spamwatch_api = PSnit.spamwatch_api
CASH_API_KEY = PSnit.CASH_API_KEY
TIME_API_KEY = PSnit.TIME_API_KEY
WALL_API = PSnit.WALL_API
LASTFM_API_KEY = PSnit.LASTFM_API_KEY
CF_API_KEY = PSnit.CF_API_KEY

SPB_MODE = psychoconfig.getboolean('SPB_MODE', False)

# SpamWatch
sw = PSnit.init_sw()

from tg_bot.modules.sql import SESSION


updater = tg.Updater(TOKEN, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10}, persistence=PostgresPersistence(SESSION))
telethn = TelegramClient(MemorySession(), APP_ID, API_HASH)
dispatcher = updater.dispatcher



# Load at end to ensure all prev variables have been set
from tg_bot.modules.helper_funcs.handlers import CustomCommandHandler

if CUSTOM_CMD and len(CUSTOM_CMD) >= 1:
    tg.CommandHandler = CustomCommandHandler


def spamfilters(text, user_id, chat_id):
    # print("{} | {} | {}".format(text, user_id, chat_id))
    if int(user_id) in SPAMMERS:
        print("Bu kullanıcı kötü amaçlı olarak işaretlenmiş!")
        return True
    else:
        return False
