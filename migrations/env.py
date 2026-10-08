from alembic import context
from sqlalchemy import create_engine, pool

from ada.config import Settings
from ada.models import Base

target_metadata = Base.metadata
url = Settings().database_url


def include_object(obj, name, type_, reflected, compare_to):
    # Native indexes and SQLite FTS5 shadow tables belong to migration 0003.
    if type_ == "table" and (name == "claim_fts" or name.startswith("claim_fts_")):
        return False
    if type_ == "index" and name == "claim_search_fts":
        return False
    return True


if context.is_offline_mode():
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, include_object=include_object
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, include_object=include_object
        )
        with context.begin_transaction():
            context.run_migrations()
