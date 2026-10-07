from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high"]


class TaskWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=5000)
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"

    @field_validator("title")
    @classmethod
    def meaningful_title(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Title must contain text")
        return value


class TaskRead(TaskWrite):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
