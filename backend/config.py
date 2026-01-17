import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()



@dataclass(frozen=True)
class Config:
    database_url: str
    auth_secret: str
    auth_token_ttl_seconds: int
    default_provider: str
    ollama_base_url: str
    ollama_model: str
    openai_compat_api_key: str | None
    openai_compat_base_url: str | None
    openai_compat_model: str | None


def load_config() -> Config:
    # 获取项目根目录的绝对路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_db_path = os.path.join(base_dir, "novels.db")
    
    return Config(
        database_url=os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}"),
        auth_secret=os.getenv("AUTH_SECRET", "change-me"),
        auth_token_ttl_seconds=int(os.getenv("AUTH_TOKEN_TTL_SECONDS", "604800")),
        default_provider=os.getenv("DEFAULT_PROVIDER", "ollama"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5"),
        openai_compat_api_key=os.getenv("OPENAI_COMPAT_API_KEY") or None,
        openai_compat_base_url=os.getenv("OPENAI_COMPAT_BASE_URL") or None,
        openai_compat_model=os.getenv("OPENAI_COMPAT_MODEL") or None,
    )

