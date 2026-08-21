from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    identifier: str
    name: str
    age: str
    role: str = "user"
