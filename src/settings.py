from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    BASE_DIR: str = Field(
        default=str(Path(__file__).resolve().parent.parent),
        alias="GITHUB_WORKSPACE",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
