from typing import Any

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class DictResponse(BaseModel):
    data: dict[str, Any]
