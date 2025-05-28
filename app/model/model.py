from pydantic.main import BaseModel

class InstagramAccount(BaseModel):
    id: str
    username: str
    password: str
    enabled: boolean
    session: str
