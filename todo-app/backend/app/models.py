from pydantic import field_validator
from sqlmodel import Field, SQLModel


def _strip(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) else value


class TodoBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)

    _strip_title = field_validator("title", mode="before")(_strip)


class Todo(TodoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    done: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None

    _strip_title = field_validator("title", mode="before")(_strip)
