import uuid

from langgraph.types import Command
from langgraph.store.sqlite import SqliteStore
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import TodoListMiddleware, ToolCallLimitMiddleware
from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends.utils import validate_path
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend

from tool import internet_search, get_current_time, append_history
import config

from news_model import NewsList
from memory_model import MemoryContext
from identity import user_namespace
from ask_user import ask_decision

model = ChatOpenAI(
    model=config.MODEL_NAME,
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.BASE_URL,
)

# DeepSeek thinking mode does not support tool_choice="required", so subagents with response_format use non-thinking mode
structured_model = ChatOpenAI(
    model=config.MODEL_NAME,
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.BASE_URL,
    extra_body={"thinking": {"type": "disabled"}},
)

# Subagents. A subagent without model / tools inherits them from the main agent.
subagents = [
    {
        "name": "news-collector",
        "description": "Collects relevant news from multiple sources",
        "system_prompt": config.NEWS_COLLECTOR_PROMPT,
        "model": structured_model,
        "middleware": [
            ToolCallLimitMiddleware(tool_name="internet_search", run_limit=10, exit_behavior="continue"),
        ],
        "response_format": NewsList,
        "tools": [internet_search, get_current_time],
    },
    {
        "name": "news-categorizer",
        "description": "Categorizes and organizes the collected news",
        "system_prompt": config.NEWS_CATEGORIZER_PROMPT,
        "model": structured_model,
        "skills": ["/skills/news-categorizer/"],
        "response_format": NewsList,
        "tools": [internet_search, get_current_time],
    },
    {
        "name": "old-news-checker",
        "description": "Checks whether news has already been reported",
        "system_prompt": config.OLD_NEWS_CHECKER_PROMPT,
        "model": structured_model,
        "skills": ["/skills/old-news-checker/"],
        "response_format": NewsList,
        "tools": [internet_search, get_current_time],
    },
    {
        "name": "report-generator",
        "description": "Writes the news report",
        "system_prompt": config.REPORT_GENERATOR_PROMPT,
        "tools": [internet_search, get_current_time],
    },
]

def protected_path(request):
    """Return True when the call targets a path that requires approval."""
    path = request.tool_call["args"].get("file_path", "")
    try:
        path = validate_path(path)
    except ValueError:
        return False
    return path.startswith(("/history/", "/report/"))

def build_agent(store=None, checkpointer=None):
    return create_deep_agent(
        model=model,
        # Tools
        tools=[internet_search, get_current_time, append_history],
        # System prompt
        system_prompt=config.SYSTEM_PROMPT,
        # Middleware, added explicitly
        middleware=[TodoListMiddleware()],
        # Runtime context schema
        context_schema=MemoryContext,
        # Memory file paths
        memory=["/memories/preferences.md"],
        # Persistent store
        store=store,
        # Backend. CompositeBackend combines several backends.
        backend=CompositeBackend(
            default=StateBackend(),            # Default: ephemeral storage
            # Routes
            routes={
                "/history/": StoreBackend(
                    namespace=lambda rt: (*user_namespace(rt), "history"),
                ),
                "/memories/": StoreBackend(
                    namespace=lambda rt: (*user_namespace(rt), "memories"),
                ),
                "/report/": StoreBackend(
                    namespace=lambda rt: (*user_namespace(rt), "report"),
                ),
                "/skills/": FilesystemBackend(root_dir="skills", virtual_mode=True),
            }
        ),
        # Human approval (interrupt before writing to history or report) is only an exercise for Chapter 9.
        # ai-news does not need it, so it is commented out. To re-enable it, uncomment interrupt_on below.
        # protected_path and the resume loop at the end of this file are kept.
        # interrupt_on={
        #     "write_file": {
        #         "allowed_decisions": ["approve", "reject"],
        #         "when": protected_path
        #     },
        #     "edit_file": {
        #         "allowed_decisions": ["approve", "reject"],
        #         "when": protected_path
        #     },
        #     "delete": {
        #         "allowed_decisions": ["approve", "reject"],
        #         "when": protected_path
        #     },
        # },
        # Permissions
        permissions=[
            # skills is read-only, and history can only be written by the append_history tool
            FilesystemPermission(
                operations=["write"],
                paths=["/skills/**", "/history/**"],
                mode="deny",
            ),
        ],
        # Resuming after an interrupt needs a checkpointer keyed by thread ID
        checkpointer=checkpointer,
        # Subagents
        subagents=subagents,
    )

# langgraph dev loads this graph. The server provides the checkpointer and store.
agent = build_agent()

if __name__ == "__main__":
    with SqliteStore.from_conn_string("news.db") as store:
        store.setup()  # Creates tables on the first run. Later calls do not recreate them.

        # Thread ID used to resume after an interrupt
        configurable = {"configurable": {"thread_id": str(uuid.uuid4())}}

        cli_agent = build_agent(store=store, checkpointer=MemorySaver())

        result = cli_agent.invoke(
            {"messages": [{"role": "user", "content": config.USER_PROMPT}]},
            config=configurable,
            version="v2",
        )

        while result.interrupts:
            interrupt_value = result.interrupts[0].value
            action_requests = interrupt_value["action_requests"]
            review_configs = interrupt_value["review_configs"]
            config_map = {cfg["action_name"]: cfg for cfg in review_configs}

            # Provide decisions in order
            decisions = []
            for action in action_requests:
                review_config = config_map[action["name"]]
                args = action.get("arguments", action.get("args", {}))
                decisions.append(ask_decision(action, review_config["allowed_decisions"]))

            result = cli_agent.invoke(
                Command(resume={"decisions": decisions}),
                config=configurable,
                version="v2",
            )

    print(result.value["messages"][-1].content)
