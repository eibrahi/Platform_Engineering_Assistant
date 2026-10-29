from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.main import app


@pytest.fixture(scope='session')
def engine():
    if not settings.test_database_url:
        pytest.exit('TEST_DATABASE_URL fehlt in .env', returncode=1)
    # Schema über die echten Migrationen aufbauen, damit Tests auch die Migrationen prüfen
    alembic_cfg = Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', settings.test_database_url.replace('%', '%%'))
    command.downgrade(alembic_cfg, 'base')
    command.upgrade(alembic_cfg, 'head')

    engine = create_engine(settings.test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine) -> Iterator[Session]:
    """Jeder Test läuft in einer Transaktion, die am Ende zurückgerollt wird."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode='create_savepoint', expire_on_commit=False)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
