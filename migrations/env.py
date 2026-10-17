from alembic import context
from sqlalchemy import create_engine, pool

from ada import (  # noqa: F401
    agent_models,
    consolidation_models,  # noqa: F401
    embedding_models,
    entity_models,
    expression_models,
    learning_models,
    login_models,
    proposal_models,
    security_models,
    stream_models,
    voice_models,
)
from ada.config import Settings
from ada.models import Base

target_metadata = Base.metadata
url = Settings().database_url


def include_object(obj, name, type_, reflected, compare_to):
    # Native indexes and SQLite FTS5 shadow tables belong to migrations 0003/0005.
    if type_ == "table" and any(
        name == root or name.startswith(root + "_") for root in ("claim_fts", "document_fts")
    ):
        return False
    if type_ == "index" and name in ("claim_search_fts", "document_search_fts"):
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
