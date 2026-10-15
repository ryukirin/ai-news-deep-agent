import os
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = os.environ["MODEL_NAME"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = os.environ["BASE_URL"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]