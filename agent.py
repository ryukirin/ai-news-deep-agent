from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware, ToolCallLimitMiddleware
from langgraph.store.sqlite import SqliteStore
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend

from tool import internet_search, get_current_time
import config

from data_model import NewsList

model = ChatOpenAI(
    model=config.MODEL_NAME,
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.BASE_URL,
)

# DeepSeek 思考模式不支持 tool_choice="required"，带 response_format 的子 Agent 改用非思考模式
structured_model = ChatOpenAI(
    model=config.MODEL_NAME,
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.BASE_URL,
    extra_body={"thinking": {"type": "disabled"}},
)

# 定义子 Agent 列表 未指定 model / tools 时自动继承主 Agent 的模型和工具
subagents = [
    {
        "name": "news-collector",
        "description": "从多个来源收集相关新闻",
        "system_prompt": config.NEWS_COLLECTOR_PROMPT,
        "model": structured_model,
        "middleware": [
            ToolCallLimitMiddleware(tool_name="internet_search", run_limit=10, exit_behavior="continue"),
        ],
        "response_format": NewsList,
    },
    {
        "name": "news-categorizer",
        "description": "对收集到的新闻进行分类和整理",
        "system_prompt": config.NEWS_CATEGORIZER_PROMPT,
        "model": structured_model,
        "response_format": NewsList,
    },
    {
        "name": "old-news-checker",
        "description": "检查是否属于过往新闻",
        "system_prompt": config.OLD_NEWS_CHECKER_PROMPT,
        "model": structured_model,
        "response_format": NewsList,
    },
    {
        "name": "report-generator",
        "description": "生成新闻报告",  
        "system_prompt": config.REPORT_GENERATOR_PROMPT,
    },
]

with SqliteStore.from_conn_string("news.db") as store:
    store.setup()  # 首次运行时建表，之后再调用不会重复建
    agent = create_deep_agent(
        model=model,
        tools=[internet_search, get_current_time],
        system_prompt=config.SYSTEM_PROMPT,
        middleware=[TodoListMiddleware()],
        backend=CompositeBackend(
            default=StateBackend(),            # 默认：临时存储
            routes={
                "/history/": StoreBackend(
                    namespace=lambda rt: (
                        (rt.server_info.user.identity,)
                        if rt.server_info else
                        ("local-user",)
                    ),
                ),
                "/report/": FilesystemBackend(root_dir="report", virtual_mode=True)
            }
        ),
        store=store,
        subagents=subagents,
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": config.USER_PROMPT}]},
    )

print(result["messages"][-1].content)
plan = result.get("todos")
if plan:
    print("Todo 列表：")
    for item in plan:
        print(f"  [{item['status']}] {item['content']}")
else:
    print("本次没有 todos 状态")