import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env") 

load_dotenv(dotenv_path=dotenv_path, override=True)

APP_HOST = os.environ.get("HOST")
APP_PORT = int(os.environ.get("PORT"))
APP_DEBUG = True if os.environ.get("DEBUG") == "True" else False
DEV_TOOLS_PROPS_CHECK = True if os.environ.get("DEBUG") == "True" else False