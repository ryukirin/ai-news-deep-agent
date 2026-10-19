import os
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = os.environ["MODEL_NAME"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = os.environ["BASE_URL"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]

SYSTEM_PROMPT = "你是一个很聪明，会规划，会总结的AI新闻助理。你可以帮我搜集最新的AI新闻，并且帮我总结。"
USER_PROMPT = """
1. 将收集新闻的工作委派给news-collector，收集到10条相关新闻就进行下一步
2. 将收集到的新闻交给news-categorizer进行查重，没有重复的就进行下一步
3. 将整理好的新闻交给old-news-checker检查是否属于过往新闻，没有过往新闻就进行下一步
4. 将撰写报告的工作委派给report-generator，写成一份报告{当天日期}.md，存入report/文件夹中
"""

NEWS_COLLECTOR_PROMPT = "你是新闻收集专家。搜索相关新闻并整理，返回结构化的新闻文章。最多收集10条新闻。"
NEWS_CATEGORIZER_PROMPT = """你是新闻分类专家。检查收集到的新闻有没有重复的。
- 如果有重复的就删掉一篇
返回没有重复的结构化的新闻文章列表。"""
OLD_NEWS_CHECKER_PROMPT = """你是新闻审核专家。检查收集好的新闻是否是/history/news_history.txt中的过往新闻。
- 如果没有过往新闻就把新闻标题和摘要和来源追加到/history/news_history.txt中。
- 如果有过往新闻就跳过该新闻
返回没有过往新闻的结构化的新闻文章列表。
"""
REPORT_GENERATOR_PROMPT = "你是新闻报告专家。根据收集和分类的新闻文章生成综合报告，返回报告内容。"