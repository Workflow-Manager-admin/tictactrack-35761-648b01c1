"""
SQLAlchemy ORM models representing database tables.
"""
from datetime import datetime
from enum import Enum  # Python enum for game status

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class GameStatus(str, Enum):  # type: ignore[misc]
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


# PUBLIC_INTERFACE
class User(Base):
    """User table."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# PUBLIC_INTERFACE
class Game(Base):
    """Game table."""

    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player_x_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player_o_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_turn = Column(String, default="X")  # "X" or "O"
    status = Column(SQLEnum(GameStatus), default=GameStatus.IN_PROGRESS)
    winner = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    player_x = relationship("User", foreign_keys=[player_x_id])
    player_o = relationship("User", foreign_keys=[player_o_id])
    moves = relationship("Move", back_populates="game")


# PUBLIC_INTERFACE
class Move(Base):
    """Move table."""

    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position = Column(Integer, nullable=False)  # 0-8
    created_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("Game", back_populates="moves")
    player = relationship("User")
