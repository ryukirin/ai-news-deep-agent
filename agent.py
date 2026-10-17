from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from langgraph.store.sqlite import SqliteStore
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend

from tool import internet_search, get_current_time
import config

model = ChatOpenAI(
    model=config.MODEL_NAME,
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.BASE_URL,
)

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