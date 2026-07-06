from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    email: str | None = None
    role: str = "user"
