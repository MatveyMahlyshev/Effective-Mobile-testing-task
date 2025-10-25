from pydantic import BaseModel

# class PermissionLevel:
#     USER = 1
#     MODERATOR = 2
#     ADMIN = 3


class EditPermission(BaseModel):
    permission: int
