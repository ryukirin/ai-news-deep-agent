import os
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = os.environ["MODEL_NAME"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
BASE_URL = os.environ["BASE_URL"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]

SYSTEM_PROMPT = "You are a smart AI news assistant that can plan and summarize. Collect the latest AI news and summarize it."
USER_PROMPT = """
1. Delegate news collection to news-collector. Move to the next step once 10 relevant news articles have been collected.
2. Pass the collected news to news-categorizer for deduplication. Move to the next step once no duplicates remain.
3. Pass the deduplicated news to old-news-checker to check for past news. Move to the next step once no past news remains.
4. Delegate report writing to report-generator. Write the report as {today's date}.md and save it in the report/ folder.
5. Call append_history to append the news used in the report to /history/news_history.txt, so that the list of past news stays complete.
"""

NEWS_COLLECTOR_PROMPT = "You are a news collection expert. Search for relevant news, organize it, and return structured news articles. Collect at most 10 news articles."
NEWS_CATEGORIZER_PROMPT = """You are a news deduplication expert.
The input is the list of news articles in the task description.
Following the criteria in the news-dedup Skill, find articles that report the same event and keep only one article from each group.
Return the deduplicated list of structured news articles."""
OLD_NEWS_CHECKER_PROMPT = """You are a news review expert.
The input is the list of news articles in the task description. Following the criteria in the history-check Skill, find the articles that duplicate the history and remove them.
Return the list of structured news articles with past news removed.
"""
REPORT_GENERATOR_PROMPT = "You are a news report expert. Write a comprehensive report from the collected and categorized news articles, and return the report content."
