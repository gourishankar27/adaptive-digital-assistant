from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADA_", env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://ada:ada@127.0.0.1:5432/ada"
    provider: Literal["ollama", "fake"] = "ollama"
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3.8:27b"
    context_tokens: int = Field(default=8192, ge=2048, le=32768)
    output_tokens: int = Field(default=512, ge=64, le=4096)
    timeout_seconds: int = Field(default=180, ge=1, le=900)
    max_parallel: int = Field(default=1, ge=1, le=4)
    prompt_bytes: int = Field(default=6000, ge=1200, le=24000)
    memory_bytes: int = Field(default=2200, ge=0, le=12000)
    retrieval_limit: int = Field(default=8, ge=1, le=16)

    @model_validator(mode="after")
    def fits_context(self):
        if self.prompt_bytes + self.output_tokens + 512 > self.context_tokens:
            raise ValueError("prompt_bytes + output_tokens + 512 must fit context_tokens")
        return self
