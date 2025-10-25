from pydantic import BaseModel


class EditPermission(BaseModel):
    permission: int
