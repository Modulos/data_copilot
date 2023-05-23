import uuid

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ORMBase(BaseModel):
    class Config:
        orm_mode = True


class Group(ORMBase):
    id: uuid.UUID
    name: str
    is_admin: bool
    description: str = ""


class CreateGroup(BaseModel):
    name: str
    description: str = ""
    is_admin: bool = False


class GroupMemberships(ORMBase):
    id: uuid.UUID
    group_id: uuid.UUID
    member_id: uuid.UUID
    group: Group


class CreateGroupMembership(BaseModel):
    group_id: uuid.UUID
    member_id: uuid.UUID


class User(ORMBase):
    id: uuid.UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    sso: bool = False
    sso_provider: str | None = None
    company: str | None = None
    is_active: bool = True
    groups: list[GroupMemberships] | None = []


class GroupList(BaseModel):
    groups: list[str]


class CreateUser(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    password: str
    is_active: bool = True
