import re
import config
from tavily import TavilyClient

from langchain.tools import ToolRuntime
from deepagents.backends.utils import create_file_data, update_file_data

from identity import user_namespace

HISTORY_FILE = "/news_history.txt"
HISTORY_LINE = re.compile(r"^\d{4}-\d{2}-\d{2} \| .+ \| .+$")

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

def append_history(lines: list[str], runtime: ToolRuntime) -> str:
    """Append news used in the report to the history file.

    Args:
        lines: One news item per entry, formatted as `YYYY-MM-DD | title | summary`.
        runtime: The tool runtime context.
    """
    lines = [line.strip() for line in lines if line.strip()]
    bad = [line for line in lines if not HISTORY_LINE.match(line)]
    if bad:
        return f"格式不符，未写入任何一条: {bad}"

    namespace = (*user_namespace(runtime), "history")
    item = runtime.store.get(namespace, HISTORY_FILE)
    old = item.value["content"] if item else ""
    old_lines = old if isinstance(old, list) else old.splitlines()

    # 已存在的行跳过，从 checkpoint 恢复时重复调用不会写入重复记录
    new = [line for line in lines if line not in old_lines]
    content = "\n".join([*old_lines, *new])
    file_data = update_file_data(item.value, content) if item else create_file_data(content)
    runtime.store.put(namespace, HISTORY_FILE, file_data)
    return f"追加 {len(new)} 条，跳过已存在的 {len(lines) - len(new)} 条"