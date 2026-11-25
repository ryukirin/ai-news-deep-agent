"""Check that two users get separate namespaces in the Store.

Start the server first (agentseek dev), then run from the project root:
    uv run --no-project python demo_users.py
"""
import sys

from langgraph_sdk import get_sync_client
from langgraph_sdk.errors import NotFoundError

URL = "http://127.0.0.1:2024"
GRAPH = "ai-news"
KEY = "/preferences.md"
USERS = {
    "demo-alice": "Preferred topics: AI chips and data centers",
    "demo-bob": "Preferred topics: AI regulation",
}
WRITE = "Use write_file to save exactly this line to /memories/preferences.md, then stop: {line}"
READ = "Use read_file to read /memories/preferences.md and reply with its exact content. If the file does not exist, reply NONE."

client = get_sync_client(url=URL, timeout=600)
results = []


def check(name, ok, detail):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")


def run_as(user, prompt):
    """Run the agent as the given user and return the final answer."""
    thread_id = client.threads.create()["thread_id"]
    state = client.runs.wait(
        thread_id,
        GRAPH,
        input={"messages": [{"role": "user", "content": prompt}]},
        context={"user_id": user},
    )
    content = state["messages"][-1]["content"]
    return content if isinstance(content, str) else str(content)


def read_memory(user):
    """Return the content of /memories/preferences.md in the user's namespace, or None."""
    try:
        item = client.store.get_item([user, "memories"], key=KEY)
    except NotFoundError:
        return None
    if item is None:
        return None
    content = item["value"]["content"]
    return content if isinstance(content, str) else "\n".join(content)


def memory_keys(user):
    return sorted(item["key"] for item in client.store.search_items([user, "memories"], limit=100)["items"])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    alice, bob = USERS
    for user in USERS:  # Start from an empty file for both demo users
        try:
            client.store.delete_item([user, "memories"], key=KEY)
        except NotFoundError:
            pass
    local_before = memory_keys("local-user")

    run_as(alice, WRITE.format(line=USERS[alice]))
    answer = run_as(bob, READ)
    first_line = answer.strip().splitlines()[0] if answer.strip() else ""
    check("Read isolation", USERS[alice] not in answer, f"{bob} reads /memories{KEY} after {alice} wrote it, answer {first_line!r}")
    run_as(bob, WRITE.format(line=USERS[bob]))

    for user, line in USERS.items():
        content = read_memory(user) or ""
        others = [other for name, other in USERS.items() if name != user]
        ok = line in content and not any(other in content for other in others)
        check(f"Namespace ({user}, memories)", ok, f"/memories{KEY} = {content.strip()!r}")

    local_after = memory_keys("local-user")
    check("Namespace (local-user, memories)", local_after == local_before, f"unchanged, files {local_after}")

    print(f"\n{sum(results)}/{len(results)} checks passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
