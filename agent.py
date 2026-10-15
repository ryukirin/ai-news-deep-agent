from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

from tool import internet_search, get_current_time
import config

model = ChatOpenAI(
    model=config.MODEL_NAME,
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.BASE_URL,
)

agent = create_deep_agent(
    model=model,
    tools=[internet_search, get_current_time],
    system_prompt="你是一个很聪明，会规划，会总结的AI新闻助理。你可以帮我搜集最新的AI新闻，并且帮我总结。",
    middleware=[TodoListMiddleware()],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "先搜一下最近的AI新闻，然后看看这些有没有重复的，最后帮我总结一下"}]},
)

print(result["messages"][-1].content)
plan = result.get("todos")
if plan:
    print("Todo 列表：")
    for item in plan:
        print(f"  [{item['status']}] {item['content']}")
else:
    print("本次没有 todos 状态")