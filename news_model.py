from pydantic import BaseModel, Field

class NewsArticle(BaseModel):
    title: str = Field(description="Title of the news article")
    content: str = Field(description="Content of the news article")
    source: str = Field(description="Source of the news article")

class NewsList(BaseModel):
    articles: list[NewsArticle] = Field(description="List of news articles")
