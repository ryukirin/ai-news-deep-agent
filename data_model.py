from pydantic import BaseModel, Field

class NewsArticle(BaseModel):
    title: str = Field(description="新闻文章标题")
    content: str = Field(description="新闻文章内容")
    source: str = Field(description="新闻文章来源")

class NewsList(BaseModel):
    articles: list[NewsArticle] = Field(description="新闻文章列表")