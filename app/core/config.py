from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings):
    PROJECT_NAME: str = "Financial Analytics Platform"
    
    # Postgres configs
    POSTGRES_USER: str = "app_user"
    POSTGRES_PASSWORD: str = "app_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5434
    POSTGRES_DB: str = "financial_db"
    
    # ClickHouse configs
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = "clickhouse_password"
    CLICKHOUSE_DB: str = "default"
    
    #Redis config
    REDIS_HOST: str = "localhost"
    REDIS_PORT : int = 6379
    
    @property
    def DATABASE_URL_ASYNCPG(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
settings = Settings()