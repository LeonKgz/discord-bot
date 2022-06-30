import os
import sys

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

# Global Languages Dictionary, mapping each command name to its respective language code
GLD = {
  "remedies": "en",
  "remedy": "en",
  "средства": "ru",
  "средство": "ru",
  "prayer": "en",
  "молитва": "ru",
}