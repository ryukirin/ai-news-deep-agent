# ai-news-deep-agent

用 [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) 搭建的 AI 新闻助理。Agent 调用 Tavily 搜索新闻，再用中文按主题汇总。

本项目是 Datawhale 课程 [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action) 的学习项目。

## 学习进度

| 章节 | 状态 |
| --- | --- |
| 第 1 章 [从 Agent Framework 到 Agent Harness](https://datawhalechina.github.io/deepagents-in-action/chapters/ch01-agent-harness/) | 已完成 |
| 第 2 章 [快速上手](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/) | 已完成 |
| 第 3 章 [虚拟文件系统](https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/) | 进行中（虚拟文件系统与七个内置文件工具） |
| 第 4 至 16 章 | 未开始 |

进度更新于 2026-10-13。

## 与课程的对应

`agent.py` 和 `tool.py` 基于第 2 章的研究助手示例修改。第 2 章内容在本项目中的位置：

| 课程内容 | 本项目 |
| --- | --- |
| 用 `ChatOpenAI` 和 `base_url` 接入 OpenAI 兼容模型 | `agent.py` |
| 自定义工具（参数类型标注、返回类型、docstring） | `tool.py` 的 `internet_search` |
| 显式加入 `TodoListMiddleware`，启用 `write_todos` 任务规划 | `agent.py` |
| LangSmith 追踪 | `.env.example` 中的 `LANGSMITH_*` 变量 |

课程示例之外的改动：

- 搜索类别固定为新闻（`topic="news"`）。
- 新增 `get_current_time` 工具，模型可以调用它获取当前日期和时间。
- 运行结束后打印 `todos` 状态，用来确认模型是否调用了 `write_todos`。
- 环境变量统一在 `config.py` 中读取，`.env` 由 `python-dotenv` 加载。

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

`requirements.txt` 没有固定版本号。2026-10-15 验证时安装的版本为 deepagents 0.7.25、langchain 1.4.6、langchain-openai 1.7.2、tavily-python 0.8.5。

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

问题写在 `agent.py` 的 `agent.invoke()` 中，当前为“先搜一下最近的AI新闻，然后看看这些有没有重复的，最后帮我总结一下”。修改 `content` 可以换成其他问题。

运行结束后，终端依次打印：

1. Agent 的最终回答。
2. `todos` 状态中的任务列表和每项任务的状态。模型没有调用 `write_todos` 时，打印“本次没有 todos 状态”。

## 已知限制

- 搜索没有限定时间范围，结果中可能出现一周以前的新闻。
- system prompt 没有规定来源要求和输出格式，部分条目没有来源链接。
- 工具没有捕获 Tavily 调用的异常，搜索出错时整个运行会中断。
- 问题写死在 `agent.py` 中，不支持命令行参数。

## 参考

- [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action)：Datawhale 开源课程，内容采用 CC BY-NC-SA 4.0 协议
- [Deep Agents 官方文档](https://docs.langchain.com/oss/python/deepagents/overview)
