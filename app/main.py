from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres import PostgresSaver

from app.assistant.graph import build_graph
from app.config import settings
from app.routers import assistant, incidents, platforms, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # checkpointer und Graph einmal beim Start erzeugen, nicht pro Request
    conn_string = settings.database_url.replace('+psycopg', '')
    with PostgresSaver.from_conn_string(conn_string) as checkpointer:
        checkpointer.setup()
        app.state.graph = build_graph(checkpointer=checkpointer)
        yield


app = FastAPI(
    title='Platform Engineering Assistant',
    description='KI-gestützter Assistent für Azure- und Databricks-Datenplattformen',
    lifespan=lifespan,
)

app.include_router(platforms.router)
app.include_router(users.router)
app.include_router(incidents.router)
app.include_router(assistant.router)


@app.get('/health', tags=['system'])
def health():
    return {'status': 'ok'}
