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


db_settings = DBSettings(
    host="host",
    host_port=1234,
    db="db",
    user="user",
    password="password",
)

"""
db_settings = DBSettings(
    host=os.environ["POSTGRESQL_HOST"],
    host_port=int(os.environ["POSTGRESQL_HOST_PORT"]),
    db=os.environ["POSTGRESQL_DB"],
    user=os.environ["POSTGRESQL_USER"],
    password=os.environ["POSTGRESQL_PASSWORD"],
)
"""
