from contextlib import asynccontextmanager

from langgraph.store.sqlite.aio import AsyncSqliteStore


# langgraph.json 的 store.path 指向这里，服务端与 python agent.py 共用 news.db
@asynccontextmanager
async def generate_store():
    async with AsyncSqliteStore.from_conn_string("news.db") as store:
        await store.setup()  # 首次运行时建表，之后再调用不会重复建
        yield store
