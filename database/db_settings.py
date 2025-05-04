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
    host="26.120.69.9",
    host_port=int("5433"),
    db="nvk_mero_db",
    user="ZloyKobra",
    password="333yKobra2007",
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
