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
LINK = re.compile(r"\]\((https?://[^)\s]+)\)")

results = []


def check(name, ok, detail):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")


def read_store(prefix):
    """Open news.db read-only and return {key: text content}."""
    with sqlite3.connect("file:news.db?mode=ro", uri=True) as conn:
        rows = conn.execute("select key, value from store where prefix = ?", (prefix,)).fetchall()
    files = {}
    for key, value in rows:
        content = json.loads(value)["content"]
        files[key] = content if isinstance(content, str) else "\n".join(content)
    return files


def find_tool_calls(value):
    """Find all tool calls in one updates event."""
    if isinstance(value, dict):
        calls = list(value.get("tool_calls") or [])
        for item in value.values():
            calls += find_tool_calls(item)
        return calls
    if isinstance(value, list):
        return [call for item in value for call in find_tool_calls(item)]
    return []


def run_agent():
    """Send the fixed input. Return the thread status, error events, subagent delegation order and files read inside subagents."""
    client = get_sync_client(url=URL, timeout=900)
    thread_id = client.threads.create()["thread_id"]
    print(f"Thread: {thread_id}")

    errors = []
    tasks = {}  # Deduplicate by tool call ID. dict keeps first-seen order.
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
        in_subagent = "|" in part.event  # Subgraph events are named updates|<namespace>
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

    check("Run finished", status == "idle" and not errors, f"thread status {status}, {len(errors)} error events")

    first_seen = list(dict.fromkeys(tasks))
    check("Subagents", first_seen == SUBAGENTS, f"delegation order {' -> '.join(map(str, first_seen))}")

    missing = [path for path in SKILLS if path not in subagent_reads]
    check("Skills", not missing, f"not read: {missing}" if missing else "both SKILL.md files read inside subagents")

    history = read_store("local-user.history")
    new_lines = history.get("/news_history.txt", "").splitlines()[len(history_before.splitlines()):]
    new_lines = [line for line in new_lines if line.strip()]
    bad_lines = [line for line in new_lines if not HISTORY_LINE.match(line.strip())]
    check("History", bool(new_lines) and not bad_lines, f"{len(new_lines)} lines added, {len(bad_lines)} with invalid format")
    check("History path", list(history) == ["/news_history.txt"], f"files under /history/: {list(history)}")

    report = read_store("local-user.report")
    written = [key for key, text in report.items() if today in key and text.strip() and text != report_before.get(key)]
    check("Report", bool(written), f"written in this run: {written}")

    links = {url for key in written for url in LINK.findall(report[key])}
    check("Report links", bool(links), f"{len(links)} links to original articles")

    print(f"\n{sum(results)}/{len(results)} checks passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
