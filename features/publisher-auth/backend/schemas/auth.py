"""Authentication request and response shapes. Owner: publisher-auth."""
from pydantic import BaseModel, ConfigDict, field_validator


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def _username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Username is required.")
        return value

    @field_validator("password")
    @classmethod
    def _password(cls, value: str) -> str:
        if not value:
            raise ValueError("Password is required.")
        return value


class PublisherOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    publisher: PublisherOut
