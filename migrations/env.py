"""Alembic environment — builds the SQLAlchemy URL from the same .env used by the app."""
from __future__ import annotations

import os
from logging.config import fileConfig
from urllib.parse import quote_plus

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

load_dotenv()

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)


def _build_url() -> str:
    user   = quote_plus(os.environ["DB_USER"])
    pwd    = quote_plus(os.environ["DB_PASS"])
    host   = os.environ["DB_HOST"]
    port   = os.getenv("DB_PORT", "1433")
    name   = os.environ["DB_NAME"]
    driver = os.getenv("DB_DRIVER", "ODBC+Driver+17+for+SQL+Server")
    trust  = os.getenv("DB_TRUST_SERVER_CERT", "no")
    return (
        f"mssql+pyodbc://{user}:{pwd}@{host}:{port}/{name}"
        f"?driver={driver}&TrustServerCertificate={trust}"
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_build_url(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_build_url(), poolclass=pool.NullPool)
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
