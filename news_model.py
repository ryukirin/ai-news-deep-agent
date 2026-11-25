from pydantic import BaseModel, Field

class NewsArticle(BaseModel):
    title: str = Field(description="Title of the news article")
    content: str = Field(description="Content of the news article")
    source: str = Field(description="Source of the news article")
    url: str = Field(description="URL of the original article, copied from the search result")
    published_date: str = Field(description="Publication date as YYYY-MM-DD, taken from the search result")

class NewsList(BaseModel):
    articles: list[NewsArticle] = Field(description="List of news articles")
