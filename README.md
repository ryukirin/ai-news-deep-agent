# ai-news-deep-agent

用 [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) 搭建的 AI 新闻助理。主 Agent 把收集、查重、旧闻比对、撰写报告四步依次委派给四个子 Agent。查重和旧闻比对的规则写在 `skills/` 下的 Skill 中。新闻用 Tavily 搜索。历史记录、报告和长期记忆按用户存在 SQLite 中，写入历史记录和报告前需要在终端确认。

本项目是 Datawhale 课程 [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action) 的学习项目。

## 学习进度

| 章节 | 状态 |
| --- | --- |
| 第 1 章 [从 Agent Framework 到 Agent Harness](https://datawhalechina.github.io/deepagents-in-action/chapters/ch01-agent-harness/) | 已完成 |
| 第 2 章 [快速上手](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/) | 已完成 |
| 第 3 章 [虚拟文件系统](https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/) | 已完成 |
| 第 4 章 [任务规划与分解](https://datawhalechina.github.io/deepagents-in-action/chapters/ch04-task-planning/) | 已完成 |
| 第 5 章 [子 Agent 与上下文隔离](https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/) | 已完成 |
| 第 6 章 [异步子 Agent](https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/) | 已跳过（选做） |
| 第 7 章 [Skills](https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/) | 已完成 |
| 第 8 章 [长期记忆](https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/) | 已完成 |
| 第 9 章 [Human-in-the-Loop](https://datawhalechina.github.io/deepagents-in-action/chapters/ch09-human-in-the-loop/) | 已完成 |
| 第 10 至 16 章 | 未开始 |

进度更新于 2026-10-29。

## 与课程的对应

`agent.py` 和 `tool.py` 基于第 2 章的研究助手示例修改，存储后端部分参照第 3 章，子 Agent 部分参照第 5 章，Skill 部分参照第 7 章，长期记忆和按用户划分存储参照第 8 章，人工审批参照第 9 章。第 2 章内容在本项目中的位置：

| 课程内容 | 本项目 |
| --- | --- |
| 用 `ChatOpenAI` 和 `base_url` 接入 OpenAI 兼容模型 | `agent.py` |
| 自定义工具（参数类型标注、返回类型、docstring） | `tool.py` 的 `internet_search` |
| 显式加入 `TodoListMiddleware`，启用 `write_todos` 任务规划 | `agent.py` |
| LangSmith 追踪 | `.env.example` 中的 `LANGSMITH_*` 变量 |

第 3 章内容在本项目中的位置：

| 课程内容 | 本项目 |
| --- | --- |
| `CompositeBackend` 按路径前缀路由 | `agent.py` |
| `StateBackend` 作为默认后端 | `agent.py` |
| `StoreBackend` 跨会话持久化 | `agent.py` 的 `/history/`、`/report/`、`/memories/` 路由 |
| `FilesystemBackend` 读写本地磁盘 | `agent.py` 的 `/skills/` 路由 |

第 5 章内容在本项目中的位置：

| 课程内容 | 本项目 |
| --- | --- |
| 字典方式定义子 Agent | `agent.py` 的 `subagents`，共 4 个 |
| 多子 Agent 协作 | `config.py` 的 `USER_PROMPT` 按顺序委派 4 个子 Agent |
| 结构化输出（`response_format`） | `news_model.py` 的 `NewsList`，用于 `news-collector`、`news-categorizer`、`old-news-checker` |
| 不同子 Agent 用不同模型 | 带 `response_format` 的 3 个子 Agent 使用 `agent.py` 中的 `structured_model` |

第 7 章内容在本项目中的位置：

| 课程内容 | 本项目 |
| --- | --- |
| SKILL.md 的结构（frontmatter 中的 `name`、`description` 和正文） | `skills/news-categorizer/news-dedup/SKILL.md`、`skills/old-news-checker/history-check/SKILL.md` |
| `/skills/` 路由到 `FilesystemBackend` | `agent.py` |
| 子 Agent 在 spec 的 `skills` 中指定 Skill 来源目录 | `agent.py`。来源目录按子 Agent 名分开，`news-categorizer` 只加载 `news-dedup`，`old-news-checker` 只加载 `history-check` |
| 只读 Skills（`FilesystemPermission` 拒绝写入 `/skills/**`） | `agent.py` 的 `permissions`。子 Agent 没有设置自己的 `permissions`，继承这条规则 |

第 8 章内容在本项目中的位置：

| 课程内容 | 本项目 |
| --- | --- |
| `memory=` 加载记忆文件 | `agent.py`，加载 `/memories/preferences.md` |
| `context_schema` 传入运行时身份 | `memory_model.py` 的 `MemoryContext`，`user_id` 默认为 `local-user` |
| namespace 函数按用户隔离数据 | `identity.py` 的 `user_namespace`。`/history/`、`/report/`、`/memories/` 的 namespace 依次为 `(用户, "history")`、`(用户, "report")`、`(用户, "memories")` |

第 9 章内容在本项目中的位置：

| 课程内容 | 本项目 |
| --- | --- |
| `interrupt_on` 配合 `when` 只对部分调用中断 | `agent.py` 的 `protected_path`。`write_file`、`edit_file`、`delete` 的目标在 `/history/` 或 `/report/` 下时中断 |
| `allowed_decisions` 限定可选决策 | 只允许 `approve` 和 `reject` |
| Checkpointer 与 `thread_id` | `MemorySaver`，每次运行生成新的 `thread_id` |
| 用 `Command(resume=...)` 恢复 | `agent.py` 末尾的循环，决策由 `ask_user.py` 的 `ask_decision` 从命令行读取 |

课程示例之外的改动：

- 搜索类别固定为新闻（`topic="news"`）。
- 新增 `get_current_time` 工具，模型可以调用它获取当前日期和时间。
- 环境变量、system prompt（`SYSTEM_PROMPT`）和用户问题（`USER_PROMPT`）统一放在 `config.py` 中，`.env` 由 `python-dotenv` 加载。
- `StoreBackend` 使用 `SqliteStore`（`news.db`），替代课程示例中的 `InMemoryStore`，历史记录在多次运行之间保留。
- `structured_model` 通过 `extra_body={"thinking": {"type": "disabled"}}` 关闭 DeepSeek 思考模式。思考模式下，结构化输出使用的 `tool_choice` 会返回 400。
- `news-collector` 加入 `ToolCallLimitMiddleware`，每次委派最多调用 `internet_search` 10 次。

## 前置条件

- Python 3.11 及以上（deepagents 0.7.25 的要求）。本项目在 Python 3.12 上运行通过。
- 支持工具调用的 OpenAI 兼容模型服务及其 API Key。
- [Tavily](https://tavily.com) API Key。
- LangSmith API Key（可选，用于追踪）。

## 安装

```bash
git clone https://github.com/ryukirin/ai-news-deep-agent.git
cd ai-news-deep-agent
python -m venv .venv
```

激活虚拟环境：

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

`requirements.txt` 没有固定版本号。2026-10-17 验证时安装的版本为 deepagents 0.7.25、langchain 1.4.6、langchain-openai 1.7.2、langgraph 1.2.15、langgraph-checkpoint-sqlite 3.1.2、tavily-python 0.8.5。

## 配置

复制 `.env.example` 为 `.env`，填入以下变量。

| 变量 | 说明 |
| --- | --- |
| `MODEL_NAME` | 模型名称 |
| `DEEPSEEK_API_KEY` | 模型服务的 API Key，其他 OpenAI 兼容服务也使用这个变量 |
| `BASE_URL` | OpenAI 兼容接口的地址 |
| `TAVILY_API_KEY` | Tavily API Key |
| `LANGSMITH_TRACING` | 是否开启 LangSmith 追踪，`.env.example` 中为 `true` |
| `LANGSMITH_API_KEY` | LangSmith API Key |
| `LANGSMITH_PROJECT` | LangSmith 项目名 |
| `LANGSMITH_ENDPOINT` | LangSmith 追踪 API 地址。`.env.example` 中为 APAC 区域，其他区域的地址见课程第 2 章 |

前四个变量缺少任何一个，启动时会报 `KeyError` 并显示变量名。不使用 LangSmith 时，把 `LANGSMITH_TRACING` 设为 `false`。

## 运行

```bash
python agent.py
```

在项目根目录运行。问题写在 `config.py` 的 `USER_PROMPT` 中，当前的步骤为：

1. 委派 `news-collector` 收集 10 条新闻。
2. 委派 `news-categorizer` 去除重复新闻。
3. 委派 `old-news-checker` 与 `/history/news_history.txt` 中的历史新闻比对，剔除过往新闻，把新新闻追加到该文件。
4. 委派 `report-generator` 撰写报告，文件名为当天日期，写入 `/report/`。

`write_file`、`edit_file` 或 `delete` 的目标在 `/history/` 或 `/report/` 下时，运行暂停，终端打印工具名、参数和可选决策：

```text
工具: write_file
参数: {"file_path": "/report/2026-10-29.md", "content": "..."}
可选决策: approve, reject
请输入决策:
```

输入 `approve` 执行这次调用。输入 `reject` 取消这次调用，之后提示输入拒绝原因（可留空），原因返回给模型。输入其他内容时要求重新输入。调用发生在子 Agent 内时同样会暂停。写入其他路径（包括 `/memories/`）不暂停。

子 Agent 的设置：

| 子 Agent | system prompt | Skill | 返回格式 | 模型 | 搜索次数上限 |
| --- | --- | --- | --- | --- | --- |
| `news-collector` | `NEWS_COLLECTOR_PROMPT` | 无 | `NewsList` | `structured_model` | 10 |
| `news-categorizer` | `NEWS_CATEGORIZER_PROMPT` | `news-dedup` | `NewsList` | `structured_model` | 无 |
| `old-news-checker` | `OLD_NEWS_CHECKER_PROMPT` | `history-check` | `NewsList` | `structured_model` | 无 |
| `report-generator` | `REPORT_GENERATOR_PROMPT` | 无 | 文本 | 与主 Agent 相同 | 无 |

子 Agent 没有指定 `tools`，继承主 Agent 的 `internet_search` 和 `get_current_time`。

2026-10-24 的一次运行用时 273 秒。`news-categorizer` 和 `old-news-checker` 都用 `read_file` 读取了自己的 SKILL.md。查重把 10 条新闻合并为 9 条，旧闻比对剔除 0 条，`old-news-checker` 把 9 条写入历史记录（58 条增至 67 条），生成 `report/2026-10-24.md`。

运行结束后，终端打印 Agent 的最终回答。

Agent 使用的路径与实际存储位置：

| Agent 中的路径 | 实际存储位置 |
| --- | --- |
| `/history/news_history.txt` | `news.db`（SQLite）的 `store` 表，namespace 为 `(用户, "history")` |
| `/report/<日期>.md` | `news.db` 的 `store` 表，namespace 为 `(用户, "report")` |
| `/memories/` 下的路径 | `news.db` 的 `store` 表，namespace 为 `(用户, "memories")` |
| `/skills/` 下的路径 | `skills/` 目录，只读 |
| 其他路径 | Agent 的 state，运行结束后不保留 |

用户由 `identity.py` 的 `user_namespace` 决定。`rt.server_info.user` 存在时用它的 `identity`，否则用 context 中的 `user_id`。`agent.py` 调用 `invoke` 时没有传 context，目前用户固定为 `local-user`。

历史记录一行一条，格式为 `日期 | 标题 | 摘要`，由 history-check 的 SKILL.md 规定。

报告不再写入 `report/` 目录。在项目根目录用下面的代码读取某一天的报告：

```python
from langgraph.store.sqlite import SqliteStore

with SqliteStore.from_conn_string("news.db") as store:
    item = store.get(("local-user", "report"), "/2026-10-29.md")
    print(item.value["content"])
```

## 已知限制

- 搜索没有限定时间范围，结果中可能出现一周以前的新闻。
- `NewsArticle.source` 只记录媒体名称，没有链接字段，报告中不含原文链接。
- 只有 `news-collector` 限制了搜索次数，主 Agent 和其他子 Agent 调用 `internet_search` 没有上限。
- 写入历史记录的要求只写在 history-check 的 SKILL.md 中。`old-news-checker` 没有读取 SKILL.md 时不会写入历史记录。
- 历史记录没有来源字段。摘要中有时会混入比对结论，比如“边界保留、降权”。
- 主 Agent 没有配置 `skills`，但能通过 `/skills/` 路由直接读取 SKILL.md。2026-10-24 的运行中，主 Agent 在委派前读了两个 SKILL.md。
- 最终回答中的条数由模型自报，可能与 `news.db` 不一致。2026-10-24 的运行自报历史记录“现共 68 行”，`news.db` 中实际非空行为 67 行。
- 工具没有捕获 Tavily 调用的异常，搜索出错时整个运行会中断。
- 问题写死在 `config.py` 中，不支持命令行参数。
- `news.db` 和 `skills/` 按启动目录的相对路径解析。在其他目录运行时，会在该目录下另建 `news.db`，并且一个 Skill 也加载不到（日志报 `path_not_found`）。
- `memory=` 只加载 `/memories/preferences.md`，不会自动创建这个文件。Agent 自己写的记忆文件名由模型决定，2026-10-29 的运行写入了 `/memories/workflow_notes.md`，下次运行不会加载。
- Checkpointer 是 `MemorySaver`，中断状态只在进程内存中。暂停时退出程序，这次运行无法恢复。
- 恢复循环只处理 `result.interrupts` 中的第一个中断。多个子 Agent 并行写入、同时产生多个中断时，LangGraph 要求按中断 ID 分别提供恢复值，当前写法会报错。
- `read_file` 默认读取 100 行。历史记录超过 100 行后，模型不分页读取时只比对前 100 行。
- 历史记录中的日期有时是新闻发生的日期，有时是写入的日期。

## 参考

- [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action)：Datawhale 开源课程，内容采用 CC BY-NC-SA 4.0 协议
- [Deep Agents 官方文档](https://docs.langchain.com/oss/python/deepagents/overview)
