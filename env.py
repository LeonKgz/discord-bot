import os
import sys
from urllib import response

import googletrans

# retrieving Discord credentials
MANKURT_TOKEN = str(os.getenv('DISCORD_TOKEN_MANKURT'))
MANASCHI_TOKEN = str(os.getenv('DISCORD_TOKEN_MANASCHI'))
GUILD = int(str(os.getenv('DISCORD_GUILD'))) if sys.argv[1] == "prod" else int(str(os.getenv('TEST_DISCORD_GUILD')))
TEST_USER = int(str(os.getenv('TEST_USER')))
ME = int(os.getenv('ME'))
MANASCHI = int(os.getenv('MANASCHI'))

# retrieving JAWSDB credentials
HOST = str(os.getenv('DB_HOST'))
USER = str(os.getenv('DB_USER'))
PASSWORD = str(os.getenv('DB_PASSWORD'))
DB = str(os.getenv('DB_DATABASE')) if sys.argv[1] == "prod" else str(os.getenv('TEST_DB_DATABASE'))

QUOTES = str(os.getenv('QUOTES_KEY'))
FOOD_KEY = str(os.getenv('FOOD_KEY'))

SENECA_API = str(os.getenv('SENECA_API_TOKEN'))

TEST_USER = int(str(os.getenv('TEST_USER')))
TEST_USER_TOKEN = str(os.getenv('TEST_USER_TOKEN'))
TEST_USER_NAME = 'Zanshin'
DOWN = str(os.getenv('DOWN'))
down = str(os.getenv('DOWN'))

# Global Languages Dictionary, mapping each command name to its respective language code
GLD = {
  "remedies": "en",
  "remedy": "en",
  "средства": "ru",
  "средство": "ru",
  "prayer": "en",
  "молитва": "ru",
}

AMNESTY_START_DAY = 1
AMNESTY_END_DAY = 4

SECOND = 1.0
MINUTE = 60.0
HOUR = 3600.0
DAY = 86400.0

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2 
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

HEALTH_CHECK_UP_START_DAY = 0
HEALTH_CHECK_UP_END_DAY = 6

HEALTH_CHECK_UP_NUMBER = 10
HEALTH_CHECK_UP_NUMBER = 1
WEIRD_BEHAVIOUR_LIMIT = 10
WEIRD_BEHAVIOUR_LIMIT = 5
DURKA_PERIOD = 3 
ROOM_NUMBER_LIMIT = 10000

HEALTH_NOTIFY = {
  "принять": "вам нужно `!принять` лекарство",
  "справку": "вам нужно получить `!справку`",
  "анализ": "вам нужно провести `!анализ` крови",
  "рентген": "вам нужно сделать `!рентген`",
  "узи": "вам нужно сделать `!узи`",
}

LANGUAGE_CODES = googletrans.LANGCODES

PRICES = {
  "rename": 2,
  "waifu": 10
}

LIMITS = {
  "waifu": 6
}

INVENTORY_NAMES = {
  "waifu": "👩"
}

# Effects of temporary service purchases in HOURS e.g. renaming a channel is locked in for 6 hour period after executed 
EFFECTS = {
  "rename": (6, HOUR, "HOUR")
  # "rename": (6, MINUTE, "MINUTE")
}

RESPONSES = {
  "mistake": "произошла ошибка! Обратитесь к Албанцу."
}
