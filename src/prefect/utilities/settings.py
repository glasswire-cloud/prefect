"""Settings for Prefect and Prefect Orion

Note that when implementing nested settings, a `default_factory` should be used
to avoid instantiating the nested settings class until runtime.
"""

from pathlib import Path
from datetime import timedelta
from pydantic import BaseSettings, Field, SecretStr
from typing import Optional, Any, Dict


class PrefectSettings(BaseSettings):
    """ "Top-level" settings that can be shared among other classes."""

    # PLEASE NOTE: unless a setting is likely to be truly global and shared among
    # other settings objects, please add new settings to the `Settings` class at
    # the bottom of this file.

    class Config:
        env_prefix = "PREFECT_"
        frozen = True

    # home
    home: Path = Path("~/.prefect").expanduser()

    # debug
    debug_mode: bool = False
    test_mode: bool = False


# instantiate the shared settings
SharedSettings = PrefectSettings()


class DataLocationSettings(BaseSettings):
    """Settings related to the Orion Data API"""

    class Config:
        env_prefix = "PREFECT_ORION_DATA_"
        frozen = True

    name: str = "default"
    scheme: str = "file"
    base_path: str = "/tmp"


class DatabaseSettings(BaseSettings):
    """Settings related to the Orion database"""

    class Config:
        env_prefix = "PREFECT_ORION_DATABASE_"
        frozen = True

    connection_url: SecretStr = f"sqlite+aiosqlite:////{SharedSettings.home}/orion.db"
    # to use an in-memory database, uncomment this line to ensure it can be
    # accessed from multiple threads. Note it can not be shared between processes.
    # connection_url: SecretStr = "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true&check_same_thread=false"
    echo: bool = False

    # statement timeout, in seconds
    timeout: Optional[float] = 1
    # statement timeout for services, in seconds
    services_timeout: Optional[float] = None


class APISettings(BaseSettings):
    """Settings related to the Orion API"""

    # a default limit for queries
    default_limit: int = 200

    host: str = "127.0.0.1"
    port: int = 5000
    uvicorn_log_level: str = "info"


class ServicesSettings(BaseSettings):
    """Settings related to Orion services"""

    class Config:
        env_prefix = "PREFECT_ORION_SERVICES_"
        frozen = True

    # run in app
    run_in_app: bool = False

    # run scheduler every 60 seconds
    scheduler_loop_seconds: float = 60
    # batch deployments in groups of 100
    scheduler_deployment_batch_size: int = 100
    # schedule up to 100 new runs per deployment
    scheduler_max_runs: int = 100
    # schedule at most three months into the future
    scheduler_max_scheduled_time: timedelta = timedelta(days=100)

    # check for new runs every X seconds
    agent_loop_seconds: float = 5
    # check for runs that are scheduled to start in the next X seconds
    agent_prefetch_seconds: int = 10


class OrionSettings(BaseSettings):
    """Settings related to Orion"""

    class Config:
        env_prefix = "PREFECT_ORION_"
        frozen = True

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    data: DataLocationSettings = Field(default_factory=DataLocationSettings)
    api: APISettings = Field(default_factory=APISettings)
    services: ServicesSettings = Field(default_factory=ServicesSettings)


class LoggingSettings(BaseSettings):
    """Settings related to Logging"""

    class Config:
        env_prefix = "PREFECT_LOGGING_"
        frozen = True

    settings_path: Path = Path(f"{SharedSettings.home}/logging.yml")


class Settings(PrefectSettings):
    """Prefect Settings"""

    # note: incorporates all settings from the PrefectSettings class

    # logging
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # orion
    orion: OrionSettings = Field(default_factory=OrionSettings)

    # the connection url for an orion instance
    orion_host: str = None


settings = Settings()


class NotSetType:
    def __eq__(self, o: object) -> bool:
        return isinstance(o, NotSetType)


NOTSET = NotSetType()


def drop_unset(**kwargs: Any) -> Dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value != NOTSET}
