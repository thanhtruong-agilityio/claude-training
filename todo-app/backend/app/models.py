from sqlmodel import Field, SQLModel


class TodoBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)


class Todo(TodoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    done: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None
