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
    consolidation_worker_enabled: bool = True
    device_enrollment_enabled: bool = False
    deletion_worker_enabled: bool = False
    private_read_limit_per_minute: int = Field(default=2400, ge=1, le=10000)
    private_write_limit_per_minute: int = Field(default=600, ge=1, le=5000)
    private_max_body_bytes: int = Field(default=524288, ge=262144, le=1048576)
    learning_threshold: int = Field(default=3, ge=3, le=10)
    embedding_enabled: bool = False
    embedding_model: Literal["embeddinggemma:300m"] = "embeddinggemma:300m"
    embedding_digest: str = Field(
        default="85462619ee721b466c5927d109d4cb765861907d5417b9109caebc4e614679f1",
        pattern=r"^[a-f0-9]{64}$",
    )
    embedding_dimensions: Literal[128, 256, 512, 768] = 768
    embedding_timeout_seconds: int = Field(default=10, ge=1, le=30)
    embedding_min_similarity: float = Field(default=0.7, ge=0, le=1, allow_inf_nan=False)

    @model_validator(mode="after")
    def fits_context(self):
        if self.prompt_bytes + self.output_tokens + 512 > self.context_tokens:
            raise ValueError("prompt_bytes + output_tokens + 512 must fit context_tokens")
        return self
