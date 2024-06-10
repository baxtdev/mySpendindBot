from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')

OPENAI_TOKEN = getenv('OPENAI_KEY')

DATABASE_URL = getenv('DATABASE_PATH')
