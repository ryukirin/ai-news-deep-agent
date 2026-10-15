import config
from tavily import TavilyClient


tavily_client = TavilyClient(api_key=config.TAVILY_API_KEY)


def internet_search(query: str, max_results: int = 5) -> dict:
    """Run a web search for the given query.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.
    """
    return tavily_client.search(
        query, 
        max_results=max_results, 
        topic="news",
    )

def get_current_time() -> str:
    """Get the current time as a string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")