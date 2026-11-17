from contextlib import asynccontextmanager

from langgraph.store.sqlite.aio import AsyncSqliteStore


# store.path in langgraph.json points here, so the server and python agent.py share news.db
@asynccontextmanager
async def generate_store():
    async with AsyncSqliteStore.from_conn_string("news.db") as store:
        await store.setup()  # Creates tables on the first run. Later calls do not recreate them.
        yield store
