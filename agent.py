import uuid

from langgraph.types import Command
from langgraph.store.sqlite import SqliteStore
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import TodoListMiddleware, ToolCallLimitMiddleware
from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends.utils import validate_path
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend

from tool import internet_search, get_current_time
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
        "skills": ["/skills/news-categorizer/"],
        "response_format": NewsList,
    },
    {
        "name": "old-news-checker",
        "description": "检查是否属于过往新闻",
        "system_prompt": config.OLD_NEWS_CHECKER_PROMPT,
        "model": structured_model,
        "skills": ["/skills/old-news-checker/"],
        "response_format": NewsList,
    },
    {
        "name": "report-generator",
        "description": "生成新闻报告",  
        "system_prompt": config.REPORT_GENERATOR_PROMPT,
    },
]

def protected_path(request):
    """定义需要审批操作的路径"""
    path = request.tool_call["args"].get("file_path", "")
    try:
        path = validate_path(path)
    except ValueError:
        return False
    return path.startswith(("/history/", "/report/"))

with SqliteStore.from_conn_string("news.db") as store:
    store.setup()  # 首次运行时建表，之后再调用不会重复建

    # 创建线程号 用来中断恢复
    configurable = {"configurable": {"thread_id": str(uuid.uuid4())}}

    agent = create_deep_agent(
        model=model,
        # 定义工具
        tools=[internet_search, get_current_time],
        # 定义系统提示词
        system_prompt=config.SYSTEM_PROMPT,
        # 显式定义中间件
        middleware=[TodoListMiddleware()],
        # 自定义上下文
        context_schema=MemoryContext,
        # 定义记忆文件路径
        memory=["/memories/preferences.md"],
        # 使用 SqliteStore 作为持久化存储
        store=store,
        # 定义后端存储 使用 CompositeBackend 组合多种后端
        backend=CompositeBackend(
            default=StateBackend(),            # 默认：临时存储
            # 路由
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
        # 将 history、report 目录下的文件写入权限限制为中断模式，防止误操作
        interrupt_on={
            "write_file": {
                "allowed_decisions": ["approve", "reject"], 
                "when": protected_path
            }, 
            "edit_file": {
                "allowed_decisions": ["approve", "reject"], 
                "when": protected_path
            }, 
            "delete": {
                "allowed_decisions": ["approve", "reject"], 
                "when": protected_path
            },
        },
        # 定义权限
        permissions=[
            # 将 skills 只读
            FilesystemPermission(
                operations=["write"],
                paths=["/skills/**"],
                mode="deny",
            ),
        ],
        # 因为要做中断恢复 所以要定义 checkpointer 获取线程 ID
        checkpointer=MemorySaver(),
        # 定义子 Agent 列表
        subagents=subagents,
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": config.USER_PROMPT}]},
        config=configurable,
        version="v2",
    )

    while result.interrupts:
        interrupt_value = result.interrupts[0].value
        action_requests = interrupt_value["action_requests"]
        review_configs = interrupt_value["review_configs"]
        config_map = {cfg["action_name"]: cfg for cfg in review_configs}

        # 按顺序提供决策
        decisions = []
        for action in action_requests:
            review_config = config_map[action["name"]]
            args = action.get("arguments", action.get("args", {}))
            decisions.append(ask_decision(action, review_config["allowed_decisions"]))

        result = agent.invoke(
            Command(resume={"decisions": decisions}),
            config=configurable,
            version="v2",
        )

print(result.value["messages"][-1].content)