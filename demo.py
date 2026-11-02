import json
import re
import sqlite3
import sys
from datetime import datetime

from langgraph_sdk import get_sync_client

import config

URL = "http://127.0.0.1:2024"
GRAPH = "ai-news"
SUBAGENTS = ["news-collector", "news-categorizer", "old-news-checker", "report-generator"]
SKILLS = [
    "/skills/news-categorizer/news-dedup/SKILL.md",
    "/skills/old-news-checker/history-check/SKILL.md",
]
HISTORY_LINE = re.compile(r"^\d{4}-\d{2}-\d{2} \| .+ \| .+$")

results = []


def check(name, ok, detail):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")


def read_store(prefix):
    """只读打开 news.db，返回 {键: 文本内容}"""
    with sqlite3.connect("file:news.db?mode=ro", uri=True) as conn:
        rows = conn.execute("select key, value from store where prefix = ?", (prefix,)).fetchall()
    files = {}
    for key, value in rows:
        content = json.loads(value)["content"]
        files[key] = content if isinstance(content, str) else "\n".join(content)
    return files


def find_tool_calls(value):
    """从一条 updates 事件中找出所有工具调用"""
    if isinstance(value, dict):
        calls = list(value.get("tool_calls") or [])
        for item in value.values():
            calls += find_tool_calls(item)
        return calls
    if isinstance(value, list):
        return [call for item in value for call in find_tool_calls(item)]
    return []


def run_agent():
    """发送固定输入，返回线程状态、错误事件、子 Agent 委派顺序和子 Agent 内读取的文件"""
    client = get_sync_client(url=URL, timeout=900)
    thread_id = client.threads.create()["thread_id"]
    print(f"线程: {thread_id}")

    errors = []
    tasks = {}  # 用工具调用 ID 去重，dict 保留首次出现的顺序
    subagent_reads = set()
    for part in client.runs.stream(
        thread_id,
        GRAPH,
        input={"messages": [{"role": "user", "content": config.USER_PROMPT}]},
        stream_mode="updates",
        stream_subgraphs=True,
    ):
        if part.event == "error":
            errors.append(part.data)
        if not part.event.startswith("updates"):
            continue
        in_subagent = "|" in part.event  # 子图事件的格式为 updates|<命名空间>
        for call in find_tool_calls(part.data):
            if not in_subagent and call["name"] == "task":
                tasks[call["id"]] = call["args"].get("subagent_type")
            if in_subagent and call["name"] == "read_file":
                subagent_reads.add(call["args"].get("file_path"))

    status = client.threads.get(thread_id)["status"]
    return status, errors, list(tasks.values()), subagent_reads


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    history_before = read_store("local-user.history").get("/news_history.txt", "")
    report_before = read_store("local-user.report")

    status, errors, tasks, subagent_reads = run_agent()

    check("运行结束", status == "idle" and not errors, f"线程状态 {status}，错误事件 {len(errors)} 个")

    first_seen = list(dict.fromkeys(tasks))
    check("子 Agent", first_seen == SUBAGENTS, f"委派顺序 {' -> '.join(map(str, first_seen))}")

    missing = [path for path in SKILLS if path not in subagent_reads]
    check("Skill", not missing, f"未读取 {missing}" if missing else "2 个 SKILL.md 都在子 Agent 内读取")

    history = read_store("local-user.history")
    new_lines = history.get("/news_history.txt", "").splitlines()[len(history_before.splitlines()):]
    new_lines = [line for line in new_lines if line.strip()]
    bad_lines = [line for line in new_lines if not HISTORY_LINE.match(line.strip())]
    check("历史记录", bool(new_lines) and not bad_lines, f"新增 {len(new_lines)} 条，格式不符 {len(bad_lines)} 条")
    check("历史记录路径", list(history) == ["/news_history.txt"], f"/history/ 下的文件 {list(history)}")

    report = read_store("local-user.report")
    written = [key for key, text in report.items() if today in key and text.strip() and text != report_before.get(key)]
    check("报告", bool(written), f"本次写入 {written}")

    print(f"\n{sum(results)}/{len(results)} 项通过")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
