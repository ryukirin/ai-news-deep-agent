# ai-news-deep-agent

English | [日本語](README.ja.md) | [中文](README.zh-CN.md)

An AI news assistant built with [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview). The main agent delegates four steps to four subagents in order: collecting news, removing duplicates, checking against past news, and writing a report. After the report is written, the main agent calls `append_history` to append the news used in the report to the history. The rules for deduplication and the past-news check are Skills under `skills/`. News is searched with Tavily. History, reports and long-term memory are stored per user in SQLite.

This is a learning project for [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action) (Deep Agents in Action), a Chinese-language course published by the Datawhale open-source community.

## Course progress

| Chapter | Status |
| --- | --- |
| Chapter 1 [From Agent Framework to Agent Harness](https://datawhalechina.github.io/deepagents-in-action/chapters/ch01-agent-harness/) | Done |
| Chapter 2 [Quick start](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/) | Done |
| Chapter 3 [Virtual file system](https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/) | Done |
| Chapter 4 [Task planning and decomposition](https://datawhalechina.github.io/deepagents-in-action/chapters/ch04-task-planning/) | Done |
| Chapter 5 [Subagents and context isolation](https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/) | Done |
| Chapter 6 [Async subagents](https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/) | Skipped (optional) |
| Chapter 7 [Skills](https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/) | Done |
| Chapter 8 [Long-term memory](https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/) | Done |
| Chapter 9 [Human-in-the-Loop](https://datawhalechina.github.io/deepagents-in-action/chapters/ch09-human-in-the-loop/) | Done |
| Chapters 10 to 16 | Skipped |

Progress updated on 2026-11-02.

## Mapping to the course

`agent.py` and `tool.py` are based on the research assistant example in Chapter 2. The storage backend follows Chapter 3, subagents follow Chapter 5, Skills follow Chapter 7, long-term memory and per-user storage follow Chapter 8, and human approval follows Chapter 9. Chapter 2 topics in this project:

| Course topic | This project |
| --- | --- |
| Connecting an OpenAI-compatible model with `ChatOpenAI` and `base_url` | `agent.py` |
| Custom tools (type annotations, return type, docstring) | `internet_search` in `tool.py` |
| Adding `TodoListMiddleware` explicitly to enable `write_todos` planning | `agent.py` |
| LangSmith tracing | `LANGSMITH_*` variables in `.env.example` |

Chapter 3 topics in this project:

| Course topic | This project |
| --- | --- |
| `CompositeBackend` routing by path prefix | `agent.py` |
| `StateBackend` as the default backend | `agent.py` |
| `StoreBackend` for persistence across sessions | `/history/`, `/report/` and `/memories/` routes in `agent.py` |
| `FilesystemBackend` for reading and writing local disk | `/skills/` route in `agent.py` |

Chapter 5 topics in this project:

| Course topic | This project |
| --- | --- |
| Defining subagents as dictionaries | `subagents` in `agent.py`, 4 in total |
| Multiple subagents working together | `USER_PROMPT` in `config.py` delegates to the 4 subagents in order |
| Structured output (`response_format`) | `NewsList` in `news_model.py`, used by `news-collector`, `news-categorizer` and `old-news-checker` |
| Different models for different subagents | The 3 subagents with `response_format` use `structured_model` in `agent.py` |

Chapter 7 topics in this project:

| Course topic | This project |
| --- | --- |
| Structure of SKILL.md (`name` and `description` in the frontmatter, plus the body) | `skills/news-categorizer/news-dedup/SKILL.md`, `skills/old-news-checker/history-check/SKILL.md` |
| Routing `/skills/` to `FilesystemBackend` | `agent.py` |
| Setting each subagent's Skill source directory in the `skills` field of its spec | `agent.py`. Source directories are split by subagent name, so `news-categorizer` loads only `news-dedup` and `old-news-checker` loads only `history-check` |
| Read-only Skills (`FilesystemPermission` denies writes to `/skills/**`) | `permissions` in `agent.py`. Subagents have no `permissions` of their own and inherit this rule |

Chapter 8 topics in this project:

| Course topic | This project |
| --- | --- |
| Loading memory files with `memory=` | `agent.py` loads `/memories/preferences.md` |
| Passing runtime identity with `context_schema` | `MemoryContext` in `memory_model.py`. `user_id` defaults to `local-user` |
| Isolating data per user with a namespace function | `user_namespace` in `identity.py`. The namespaces of `/history/`, `/report/` and `/memories/` are `(user, "history")`, `(user, "report")` and `(user, "memories")` |

Chapter 9 topics in this project:

| Course topic | This project |
| --- | --- |
| `interrupt_on` with `when` to interrupt only some calls | `protected_path` in `agent.py`. Interrupts when `write_file`, `edit_file` or `delete` targets a path under `/history/` or `/report/` |
| Limiting choices with `allowed_decisions` | Only `approve` and `reject` are allowed |
| Checkpointer and `thread_id` | `MemorySaver`, with a new `thread_id` for each run |
| Resuming with `Command(resume=...)` | The loop at the end of `agent.py`. `ask_decision` in `ask_user.py` reads decisions from the command line |

Human approval is implemented only as a Chapter 9 exercise. ai-news writes only history and reports and does not need approval, so `interrupt_on` in `agent.py` is commented out and runs do not pause. Uncomment it to re-enable approval. `protected_path`, the resume loop and `ask_user.py` are kept.

Changes beyond the course examples:

- The search topic is fixed to news (`topic="news"`).
- A `get_current_time` tool lets the model get the current date and time.
- An `append_history` tool appends the news used in the report to `/history/news_history.txt`. Each line must be `YYYY-MM-DD | title | summary`. If any line does not match, the whole batch is rejected and a format error is returned. Lines identical to existing ones are skipped. The tool writes to the Store directly through the `store` of `ToolRuntime`, without going through `write_file`.
- `permissions` also denies writes to `/history/**`, and subagents inherit this rule. `write_file`, `edit_file` and `delete` on the history return permission denied, so the history can only be appended through `append_history`.
- Environment variables, the system prompt (`SYSTEM_PROMPT`) and the user prompt (`USER_PROMPT`) are all in `config.py`. `.env` is loaded by `python-dotenv`.
- `StoreBackend` uses `SqliteStore` (`news.db`) instead of the `InMemoryStore` in the course example, so the history is kept between runs.
- `structured_model` turns off DeepSeek thinking mode with `extra_body={"thinking": {"type": "disabled"}}`. In thinking mode, the `tool_choice` used for structured output returns 400.
- `news-collector` has `ToolCallLimitMiddleware`, which limits each delegation to 10 `internet_search` calls.

## Prerequisites

- Python 3.11 or later (required by deepagents 0.7.25). Tested on Python 3.12.
- An OpenAI-compatible model service that supports tool calling, and its API key.
- A [Tavily](https://tavily.com) API key.
- A LangSmith API key (optional, for tracing).
- `agentseek dev` also needs the AgentSeek CLI (`uv tool install agentseek`) and uv, both on `PATH`. Tested with agentseek 0.1.6 and uv 0.13.0.

## Installation

```bash
git clone https://github.com/ryukirin/ai-news-deep-agent.git
cd ai-news-deep-agent
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` is generated from `requirements.in` and pins every dependency, including deepagents 0.7.25, langchain 1.4.6, langchain-openai 1.7.2, langgraph 1.2.15, langgraph-checkpoint-sqlite 3.1.2, tavily-python 0.8.5, langgraph-cli 0.4.40, langgraph-api 0.17.0 and langgraph-runtime-inmem 0.37.0.

To update the dependencies, edit `requirements.in` and regenerate:

```bash
uv pip compile requirements.in --universal --python-version 3.11 --no-annotate -o requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in the following variables.

| Variable | Description |
| --- | --- |
| `MODEL_NAME` | Model name |
| `DEEPSEEK_API_KEY` | API key of the model service. Other OpenAI-compatible services use this variable too |
| `BASE_URL` | Base URL of the OpenAI-compatible API |
| `TAVILY_API_KEY` | Tavily API key |
| `LANGSMITH_TRACING` | Whether LangSmith tracing is on. `true` in `.env.example` |
| `LANGSMITH_API_KEY` | LangSmith API key |
| `LANGSMITH_PROJECT` | LangSmith project name |
| `LANGSMITH_ENDPOINT` | LangSmith tracing API endpoint. `.env.example` uses the APAC region. Endpoints for other regions are listed in Chapter 2 of the course |

If any of the first four variables is missing, startup fails with a `KeyError` that shows the variable name. If you do not use LangSmith, set `LANGSMITH_TRACING` to `false`.

## Usage

```bash
python agent.py
```

Run it from the project root. The prompt is `USER_PROMPT` in `config.py`, with these steps:

1. Delegate to `news-collector` to collect 10 news articles.
2. Delegate to `news-categorizer` to remove duplicates.
3. Delegate to `old-news-checker` to compare against the past news in `/history/news_history.txt` and remove past news.
4. Delegate to `report-generator` to write the report, named after the current date, into `/report/`.
5. Call `append_history` to append the news used in the report to `/history/news_history.txt`.

Runs do not pause. With `interrupt_on` re-enabled, a run pauses when `write_file`, `edit_file` or `delete` targets a path under `/history/` or `/report/`, and the terminal prints the tool name, arguments and allowed decisions:

```text
Tool: write_file
Args: {"file_path": "/report/2026-10-29.md", "content": "..."}
Allowed decisions: approve, reject
Enter a decision:
```

Enter `approve` to run the call. Enter `reject` to cancel it. You are then asked for a reason (optional), which is returned to the model. Any other input is asked again. Calls inside subagents pause the same way. Writes to other paths (including `/memories/`) do not pause.

Writes to `/history/` are denied. `write_file`, `edit_file` and `delete` on `/history/` still pause, and return permission denied after approval. `append_history` is not in `interrupt_on` and does not pause.

Subagent settings:

| Subagent | System prompt | Skill | Return format | Model | Search limit |
| --- | --- | --- | --- | --- | --- |
| `news-collector` | `NEWS_COLLECTOR_PROMPT` | None | `NewsList` | `structured_model` | 10 |
| `news-categorizer` | `NEWS_CATEGORIZER_PROMPT` | `news-dedup` | `NewsList` | `structured_model` | None |
| `old-news-checker` | `OLD_NEWS_CHECKER_PROMPT` | `history-check` | `NewsList` | `structured_model` | None |
| `report-generator` | `REPORT_GENERATOR_PROMPT` | None | Text | Same as the main agent | None |

The `tools` of each subagent are set explicitly to `internet_search` and `get_current_time`, without `append_history`.

A run on 2026-10-24 took 273 seconds. `news-categorizer` and `old-news-checker` each read their own SKILL.md with `read_file`. Deduplication merged 10 articles into 9, the past-news check removed 0, `old-news-checker` wrote 9 lines to the history (58 to 67), and `report/2026-10-24.md` was generated.

When the run finishes, the terminal prints the agent's final answer.

Paths used by the agent and where they are stored:

| Path in the agent | Storage |
| --- | --- |
| `/history/news_history.txt` | `store` table in `news.db` (SQLite), namespace `(user, "history")` |
| `/report/<date>.md` | `store` table in `news.db`, namespace `(user, "report")` |
| Paths under `/memories/` | `store` table in `news.db`, namespace `(user, "memories")` |
| Paths under `/skills/` | `skills/` directory, read-only |
| Other paths | Agent state, discarded after the run |

The user is determined by `user_namespace` in `identity.py`. If `rt.server_info.user` exists, its `identity` is used. Otherwise `user_id` from the context is used. `agent.py` does not pass a context to `invoke`, so the user is currently always `local-user`.

The history has one news item per line in the format `date | title | summary`, where the date is a single `YYYY-MM-DD`. `append_history` validates the format on write.

Reports are no longer written to the `report/` directory. To read the report for a given day, run the following from the project root:

```python
from langgraph.store.sqlite import SqliteStore

with SqliteStore.from_conn_string("news.db") as store:
    item = store.get(("local-user", "report"), "/2026-10-29.md")
    print(item.value["content"])
```

## Running the backend server

```bash
agentseek doctor
agentseek dev
```

Run these from the project root. `agentseek dev` checks `uv`, the required files and the first four variables in `.env` according to `.agentseek/lifecycle.toml`, then runs `uv run --no-project langgraph dev --no-browser --allow-blocking --port 2024`. `uv run` uses `.venv` in the project root, so the virtual environment does not need to be activated. The server is backend only, with no frontend.

| URL | Description |
| --- | --- |
| `http://127.0.0.1:2024` | LangGraph API. The graph is named `ai-news` (see `langgraph.json`) |
| `http://127.0.0.1:2024/ok` | Health check, requested by `agentseek doctor --live` |
| `http://127.0.0.1:2024/docs` | API documentation |

When the dependencies change, run `agentseek task sync`, which is equivalent to `uv pip install -r requirements.txt`.

Differences between the backend server and `python agent.py`:

| Item | `python agent.py` | `agentseek dev` |
| --- | --- | --- |
| User prompt | `USER_PROMPT` in `config.py` | Sent by the client in the request. `USER_PROMPT` is not read |
| Store | `SqliteStore` (`news.db`) | `AsyncSqliteStore` in `news_store.py` (same `news.db`) |
| Checkpointer | `MemorySaver` | Provided by the server, data in `.langgraph_api/` |
| Human approval, when re-enabled | `ask_user.py` reads decisions from the terminal | The client submits `Command(resume=...)` through the API |

Without authentication the user is also `local-user`, so the server can read the history, reports and memories written by `python agent.py`.

`--allow-blocking` turns off blocking-call detection in the dev server. The deepagents permission check calls `Path.resolve()` synchronously inside an async tool, and without this flag `ls` raises `BlockingError`. Use this flag only for local development.

Verified on 2026-11-02 with Windows 11, Python 3.12.10 and deepagents 0.7.25: `ls` returned normally, and `news-categorizer` loaded its Skill and merged 2 duplicate articles into 1. With `interrupt_on` enabled, the full four-step pipeline passed: 20 articles collected, 20 after deduplication, 1 removed by the past-news check, history grew from 10 to 29 lines, and `/report/2026-11-02.md` was generated. With `interrupt_on` commented out, writes to `/report/` no longer paused.

## Reproducible demo

The demo checks that one application uses 3 capabilities together: subagent delegation, per-subagent Skill loading, and persisting history and reports in the Store. The input is fixed to `USER_PROMPT` in `config.py`. News changes every day, so the checks cover only the flow and what was written.

Run it in a clean clone, where `news.db` is empty. On an existing `news.db`, the history keeps growing and the report for the current day is overwritten.

```powershell
git clone https://github.com/ryukirin/ai-news-deep-agent.git
cd ai-news-deep-agent
python -m venv .venv
agentseek task sync
Copy-Item .env.example .env
```

Fill in the first four variables in `.env`, then start the server:

```powershell
agentseek doctor
agentseek dev
```

In another terminal, run from the project root:

```powershell
uv run --no-project python demo.py
```

`agentseek task sync` and `uv run` prefer the environment that `VIRTUAL_ENV` points to. Do not activate another virtual environment before running them.

The longest file in `.venv` (from anthropic 1.14.0) has a path of 132 characters relative to the project root. If long paths are not enabled on Windows (`LongPathsEnabled=0`), the project root path must be 126 characters or shorter. Otherwise the server fails to start with `ModuleNotFoundError: No module named 'anthropic.types.beta...'`.

`demo.py` sends the fixed input, waits for the run to finish, and checks the following. The exit code is 0 if all checks pass and 1 otherwise.

| Check | Passes when |
| --- | --- |
| Run finished | Thread status is `idle` with no error events |
| Subagents | The main agent first delegates in the order `news-collector`, `news-categorizer`, `old-news-checker`, `report-generator` |
| Skills | Both SKILL.md files are read with `read_file` inside subagents |
| History | At least 1 line is added to `news.db`, each in the format `date \| title \| summary` |
| History path | `/history/` contains only `news_history.txt` |
| Report | A non-empty report whose file name contains the current date is written to `news.db` |

Result on 2026-11-17 with Windows 11 and Python 3.12.10, starting from an empty `news.db`, in 2 minutes 16 seconds:

```text
PASS  Run finished: thread status idle, 0 error events
PASS  Subagents: delegation order news-collector -> news-categorizer -> old-news-checker -> report-generator
PASS  Skills: both SKILL.md files read inside subagents
PASS  History: 27 lines added, 0 with invalid format
PASS  History path: files under /history/: ['/news_history.txt']
PASS  Report: written in this run: ['/2026-11-17.md']

6/6 checks passed
```

In this run, the main agent called `append_history` once after the report was written, with 27 lines, and all 27 were written. The report and the history were written in English.

Results depend on the model output, so some checks can fail. In a run on 2026-11-02, the model wrote the date as `2026-10-30/31` and the history check failed. `append_history` now validates the date format and does not write lines that do not match.

## Known limitations

- Running twice on the same day overwrites `/report/<date>.md`, and the previous version cannot be restored.
- Search has no time range, so results can include news older than a week.
- `NewsArticle.source` stores only the outlet name, with no link field, so reports do not include links to the original articles.
- Only `news-collector` has a search limit. The main agent and the other subagents can call `internet_search` without limit.
- Writing the history depends on the main agent calling `append_history` in step 5 of `USER_PROMPT`. Nothing is written if it does not.
- The history has no source field. Summaries sometimes include comparison notes from the model.
- The main agent has no `skills` configured, but can read SKILL.md directly through the `/skills/` route. In the run on 2026-10-24, the main agent read both SKILL.md files before delegating.
- Counts in the final answer are reported by the model and can differ from `news.db`. The run on 2026-10-24 reported 68 history lines, while `news.db` had 67 non-empty lines.
- The tool does not catch exceptions from Tavily, so a search error stops the whole run.
- The prompt is hard-coded in `config.py`, with no command-line arguments.
- The output language of reports and the history follows the prompt language and is fixed to English. It cannot be configured.
- `news.db` and `skills/` are resolved relative to the working directory. Running from another directory creates a separate `news.db` there and loads no Skills (the log shows `path_not_found`).
- `memory=` loads only `/memories/preferences.md` and does not create the file. The model chooses the names of memory files it writes. The run on 2026-10-29 wrote `/memories/workflow_notes.md`, which the next run does not load.
- Without approval, the paths and content the model writes to `/report/` and `/memories/` are not reviewed by a person.
- The limit of 10 articles for `news-collector` is only in the prompt. The run on 2026-11-02 collected 20.
- With `interrupt_on` enabled, the checkpointer of `python agent.py` is `MemorySaver`, so the interrupt state lives only in process memory. Exiting while paused makes the run unrecoverable.
- With `interrupt_on` enabled, the resume loop handles only the first interrupt in `result.interrupts`. When several subagents write in parallel and raise several interrupts at once, LangGraph requires a resume value for each interrupt ID, and the current code raises an error.
- `read_file` reads 100 lines by default. Once the history exceeds 100 lines, the model compares only the first 100 unless it reads page by page.
- Dates in the history are sometimes the date of the news and sometimes the date it was written.

## References

- [Deep Agents 实战](https://github.com/datawhalechina/deepagents-in-action): Datawhale open-source course, licensed under CC BY-NC-SA 4.0
- [Deep Agents documentation](https://docs.langchain.com/oss/python/deepagents/overview)
