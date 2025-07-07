from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers_auth import router as auth_router
from .routers_games import router as games_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TicTacToe Backend",
    description="RESTful API for TicTacToe game with authentication and history.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"message": "Healthy"}

# Include routers so they appear in OpenAPI docs
app.include_router(auth_router)
app.include_router(games_router)
