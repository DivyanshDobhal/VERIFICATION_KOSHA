from fastapi import HTTPException, status, Depends
from typing import List
from app.security.authentication import get_current_user_token

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, token_data: dict = Depends(get_current_user_token)) -> dict:
        user_role = token_data.get("role")
        if not user_role or user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {self.allowed_roles}, your role: {user_role}",
            )
        return token_data

# Common role dependencies
require_admin = RoleChecker(["admin"])
require_supervisor = RoleChecker(["admin", "supervisor"])
require_operator = RoleChecker(["admin", "operator", "supervisor"])
