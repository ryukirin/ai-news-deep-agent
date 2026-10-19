# ai-news-deep-agent

用 [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) 搭建的 AI 新闻助理。主 Agent 把收集、查重、旧闻比对、撰写报告四步依次委派给四个子 Agent。新闻用 Tavily 搜索，历史记录存在 SQLite 中，报告写入 `report/` 目录。

本项目是 Datawhale 课程 [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action) 的学习项目。

## 学习进度

| 章节 | 状态 |
| --- | --- |
| 第 1 章 [从 Agent Framework 到 Agent Harness](https://datawhalechina.github.io/deepagents-in-action/chapters/ch01-agent-harness/) | 已完成 |
| 第 2 章 [快速上手](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/) | 已完成 |
| 第 3 章 [虚拟文件系统](https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/) | 已完成 |
| 第 4 章 [任务规划与分解](https://datawhalechina.github.io/deepagents-in-action/chapters/ch04-task-planning/) | 已完成 |
| 第 5 章 [子 Agent 与上下文隔离](https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/) | 已完成 |
| 第 6 至 16 章 | 未开始 |

进度更新于 2026-10-19。

## 与课程的对应

`agent.py` 和 `tool.py` 基于第 2 章的研究助手示例修改，存储后端部分参照第 3 章，子 Agent 部分参照第 5 章。第 2 章内容在本项目中的位置：

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
| `StoreBackend` 跨会话持久化，本地运行时 namespace 兜底为 `("local-user",)` | `agent.py` 的 `/history/` 路由 |
| `FilesystemBackend` 写入本地磁盘 | `agent.py` 的 `/report/` 路由 |

第 5 章内容在本项目中的位置：

| 课程内容 | 本项目 |
| --- | --- |
| 字典方式定义子 Agent | `agent.py` 的 `subagents`，共 4 个 |
| 多子 Agent 协作 | `config.py` 的 `USER_PROMPT` 按顺序委派 4 个子 Agent |
| 结构化输出（`response_format`） | `data_model.py` 的 `NewsList`，用于 `news-collector`、`news-categorizer`、`old-news-checker` |
| 不同子 Agent 用不同模型 | 带 `response_format` 的 3 个子 Agent 使用 `agent.py` 中的 `structured_model` |

课程示例之外的改动：

- 搜索类别固定为新闻（`topic="news"`）。
- 新增 `get_current_time` 工具，模型可以调用它获取当前日期和时间。
- 运行结束后打印 `todos` 状态，用来确认模型是否调用了 `write_todos`。
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
4. 委派 `report-generator` 撰写报告，文件名为当天日期，写入 `report/` 目录。

子 Agent 的设置：

| 子 Agent | system prompt | 返回格式 | 模型 | 搜索次数上限 |
| --- | --- | --- | --- | --- |
| `news-collector` | `NEWS_COLLECTOR_PROMPT` | `NewsList` | `structured_model` | 10 |
| `news-categorizer` | `NEWS_CATEGORIZER_PROMPT` | `NewsList` | `structured_model` | 无 |
| `old-news-checker` | `OLD_NEWS_CHECKER_PROMPT` | `NewsList` | `structured_model` | 无 |
| `report-generator` | `REPORT_GENERATOR_PROMPT` | 文本 | 与主 Agent 相同 | 无 |

子 Agent 没有指定 `tools`，继承主 Agent 的 `internet_search` 和 `get_current_time`。

2026-10-19 的一次运行用时 184 秒，4 个子 Agent 各委派 1 次，共搜索 10 次，历史记录新增 12 条（44 条增至 56 条），生成 `report/2026-10-19.md`。

运行结束后，终端依次打印：

1. Agent 的最终回答。
2. `todos` 状态中的任务列表和每项任务的状态。模型没有调用 `write_todos` 时，打印“本次没有 todos 状态”。

Agent 使用的路径与实际存储位置：

| Agent 中的路径 | 实际存储位置 |
| --- | --- |
| `/history/news_history.txt` | `news.db`（SQLite）的 `store` 表，namespace 为 `local-user` |
| `/report/<日期>.md` | `report/<日期>.md` |
| 其他路径 | Agent 的 state，运行结束后不保留 |

## 已知限制

- 搜索没有限定时间范围，结果中可能出现一周以前的新闻。
- `NewsArticle.source` 只记录媒体名称，没有链接字段，报告中不含原文链接。
- 只有 `news-collector` 限制了搜索次数，主 Agent 和其他子 Agent 调用 `internet_search` 没有上限。
- 历史记录由哪个 Agent 写入取决于模型。2026-10-19 的运行中由主 Agent 写入，条目里没有 `OLD_NEWS_CHECKER_PROMPT` 要求的来源。
- 工具没有捕获 Tavily 调用的异常，搜索出错时整个运行会中断。
- 问题写死在 `config.py` 中，不支持命令行参数。
- `news.db` 和 `report/` 按启动目录的相对路径创建，在其他目录运行会在该目录下另建一份。
- `read_file` 默认读取 100 行。历史记录超过 100 行后，模型不分页读取时只比对前 100 行。
- 历史记录中的日期有时是新闻发生的日期，有时是写入的日期。

## 参考

- [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action)：Datawhale 开源课程，内容采用 CC BY-NC-SA 4.0 协议
- [Deep Agents 官方文档](https://docs.langchain.com/oss/python/deepagents/overview)
