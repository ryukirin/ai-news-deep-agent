import os
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = os.environ["MODEL_NAME"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = os.environ["BASE_URL"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]

SYSTEM_PROMPT = "你是一个很聪明，会规划，会总结的AI新闻助理。你可以帮我搜集最新的AI新闻，并且帮我总结。"
USER_PROMPT = """
1. 先搜一下最近的AI新闻
2. 看看这些搜索结果中有没有重复的
3. 检查这些新闻和之前的新闻有没有重复的，过往新闻在/history/news_history.txt中
    3.1 如果没有重复的就把新闻摘要和标题追加到/history/news_history.txt中
    3.2 如果有重复的就跳过该新闻
4. 最后帮我总结一下，写成一份报告{当天日期}.md，存入report/文件夹中
"""