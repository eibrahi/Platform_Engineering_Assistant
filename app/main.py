from fastapi import FastAPI

from app.routers import platforms

app = FastAPI(
    title='Platform Engineering Assistant',
    description='KI-gestützter Assistent für Azure- und Databricks-Datenplattformen',
)

app.include_router(platforms.router)


@app.get('/health', tags=['system'])
def health():
    return {'status': 'ok'}
