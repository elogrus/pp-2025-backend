import os
from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv
from pydantic import BaseModel


class DBSettings(BaseModel):
    """Настройки подключения к базе данных."""

    host: str
    host_port: int
    db: str
    user: str
    password: str
