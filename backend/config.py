from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LXGA_", env_file=".env", extra="ignore")

    db_path: Path = PROJECT_ROOT / "data" / "demo" / "liu_xi_growth_analytics.duckdb"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    demo_users: int = 100_000
    demo_seed: int = 42
    auto_generate_demo: bool = True
    copilot_narrative_mode: Literal["deterministic", "ollama"] = "deterministic"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_timeout_seconds: float = 8.0

    @property
    def resolved_db_path(self) -> Path:
        if self.db_path.is_absolute():
            return self.db_path
        return (PROJECT_ROOT / self.db_path).resolve()


settings = Settings()
