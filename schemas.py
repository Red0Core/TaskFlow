from pydantic import BaseModel, Field, ConfigDict

class TaskBase(BaseModel):
    title: str
    description: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: None | str = Field(None, description="Название задачи")
    description: None | str = Field(None, description="Описание задачи")
    is_completed: None | bool = Field(None, description="Выполнена ли задача")

class TaskPut(TaskUpdate):
    title: str
    description: str
    is_completed: bool

class TaskResponse(TaskBase):
    id: int
    is_completed: bool

    class Config:
        from_attributes = True


class UserInModel(BaseModel):
    username: str = Field(description="Имя пользователя")
    password: str = Field(
        description="Пароль пользователя (не сохраняется в открытом виде)",
        min_length=8
    )

class UserModel(BaseModel):
    id: int = Field(description="Айди пользователя")
    tasks: list[TaskResponse] = Field(
        description="Список задач, принадлежащих пользователю."
    )

    model_config = ConfigDict(from_attributes=True)