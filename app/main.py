from fastapi import FastAPI

from app.routers import incidents, platforms, users

app = FastAPI(
    title='Platform Engineering Assistant',
    description='KI-gestützter Assistent für Azure- und Databricks-Datenplattformen',
)

app.include_router(platforms.router)
app.include_router(users.router)
app.include_router(incidents.router)


@app.get('/health', tags=['system'])
def health():
    return {'status': 'ok'}
