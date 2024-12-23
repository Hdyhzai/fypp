from pydantic import BaseModel

class User(BaseModel):
    uuid: str
    fullname: str
    email: str
    password: str
    created_at: str