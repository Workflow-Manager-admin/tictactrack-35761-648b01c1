"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    username: Optional[str] = None


# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=5, max_length=100)


class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True


# Game related
class MoveCreate(BaseModel):
    position: int = Field(..., ge=0, le=8, description="Board position 0-8")


class MoveRead(BaseModel):
    id: int
    player_id: int
    position: int
    created_at: datetime

    class Config:
        orm_mode = True


class GameCreate(BaseModel):
    opponent_username: Optional[str] = Field(
        None, description="Username of opponent. If omitted, play against yourself."
    )


class GameRead(BaseModel):
    id: int
    player_x_id: int
    player_o_id: int
    current_turn: str
    status: str
    winner: Optional[str]
    created_at: datetime
    moves: List[MoveRead]

    class Config:
        orm_mode = True
