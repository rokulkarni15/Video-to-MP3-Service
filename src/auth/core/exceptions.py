from fastapi import HTTPException, status

class AuthError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class CredentialsError(AuthError):
    def __init__(self):
        super().__init__("Could not validate credentials")

class InactiveUserError(AuthError):
    def __init__(self):
        super().__init__("Inactive user")

class DuplicateUserError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )