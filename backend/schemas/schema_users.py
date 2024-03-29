from pydantic import BaseModel


class User(BaseModel):
    id: int | None = None
    name: str
    username: str
    email: str
    city: str | None = None
    birthdate: str | None = None
    preferred_language: str
    gender: int
    access_type: int
    photo_path: str | None = None
    photo_path_aux: str | None = None
    is_active: int

    class Config:
        orm_mode = True


class UserCreate(User):
    password: str


class UserMe(User):
    id: int
    is_strava_linked: int | None = None

class UserEditPassword(BaseModel):
    id: int
    password: str