from pydantic import BaseModel, EmailStr
from typing import Optional, List

class AssignGroupRequest(BaseModel):

    id: str

    grupo: str