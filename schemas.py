from pydantic import BaseModel, Field, ConfigDict

class TaskBase(BaseModel):
    title: str = Field(..., description="Название задачи")
    description: str = Field(..., description="Описание задачи")
    
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

    model_config = ConfigDict(
        from_attributes = True
    )