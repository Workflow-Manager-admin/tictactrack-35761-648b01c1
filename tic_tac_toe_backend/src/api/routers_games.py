"""
Game management router: creating games, making moves, retrieving game state & history.
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import auth, models, schemas
from .auth import get_db

router = APIRouter(prefix="/games", tags=["games"])


def determine_winner(moves: list[models.Move]) -> str | None:
    """Return 'X', 'O', or None depending on board state."""
    board = [""] * 9
    for mv in moves:
        board[mv.position] = "X" if mv.player_id == mv.game.player_x_id else "O"
    winning_combinations = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]
    for a, b, c in winning_combinations:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if "" not in board:
        return "DRAW"
    return None


@router.post(
    "/new",
    response_model=schemas.GameRead,
    summary="Start a new game",
    status_code=201,
)
def start_game(
    game_in: schemas.GameCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(get_db),
):
    opponent = (
        db.query(models.User).filter(models.User.username == game_in.opponent_username).first()
        if game_in.opponent_username
        else current_user
    )
    if not opponent:
        raise HTTPException(status_code=404, detail="Opponent not found")

    game = models.Game(player_x_id=current_user.id, player_o_id=opponent.id)
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@router.post(
    "/{game_id}/move",
    response_model=schemas.GameRead,
    summary="Make a move in a game",
)
def make_move(
    game_id: int,
    move_in: schemas.MoveCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(get_db),
):
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != models.GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Game finished")

    # Determine role
    player_role = "X" if current_user.id == game.player_x_id else "O"
    if player_role != game.current_turn:
        raise HTTPException(status_code=400, detail="Not your turn")

    # Validate position
    existing_positions = {m.position for m in game.moves}
    if move_in.position in existing_positions:
        raise HTTPException(status_code=400, detail="Position already taken")

    move = models.Move(game_id=game.id, player_id=current_user.id, position=move_in.position)
    db.add(move)
    db.commit()
    db.refresh(game)

    # Update game status
    winner = determine_winner(game.moves)
    if winner:
        game.status = models.GameStatus.FINISHED
        game.winner = winner if winner != "DRAW" else None
    else:
        game.current_turn = "O" if game.current_turn == "X" else "X"

    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@router.get(
    "/{game_id}",
    response_model=schemas.GameRead,
    summary="Get current state of a game",
)
def get_game(
    game_id: int,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(get_db),
):
    game = (
        db.query(models.Game)
        .filter(models.Game.id == game_id)
        .filter(
            (models.Game.player_x_id == current_user.id)
            | (models.Game.player_o_id == current_user.id)
        )
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found or not authorized")
    return game


@router.get(
    "/history",
    response_model=List[schemas.GameRead],
    summary="List game history for current user",
)
def history(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(get_db),
):
    games = (
        db.query(models.Game)
        .filter(
            (models.Game.player_x_id == current_user.id)
            | (models.Game.player_o_id == current_user.id)
        )
        .order_by(models.Game.created_at.desc())
        .all()
    )
    return games
