from .databases import (
    BaseDatabaseSettings,
    DBEngineEnum,
    DjangoDatabases,
    PostgresDatabaseSettings,
    SqliteDatabaseSettings,
)


def get_django_dbs() -> DjangoDatabases:
    """Get the Django database settings."""
    base_settings = BaseDatabaseSettings()

    if base_settings.engine == DBEngineEnum.POSTGRES:
        db_settings = PostgresDatabaseSettings()
    else:
        db_settings = SqliteDatabaseSettings()

    return DjangoDatabases(default=db_settings)


def get_django_db_dict() -> dict:
    """Get the Django database settings as a dictionary."""
    db = get_django_dbs()
    return db.model_dump(mode="json", by_alias=True)
