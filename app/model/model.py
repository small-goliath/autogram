from pydantic.main import BaseModel

class ActionTarget(BaseModel):
    username: str
    link: str