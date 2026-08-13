from pydantic import BaseModel


class DeleteUserRequest(BaseModel):
    id: str
