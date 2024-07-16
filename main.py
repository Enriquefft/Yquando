"""Main API module for the chatbot."""

# ruff: noqa: B008
from typing import Generator

from fastapi import Depends, FastAPI, Form
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ai import get_response

# Internal imports
from models import Conversation, SessionLocal
from wsp import logger, send_message

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"msg": "up & running"}


# Dependency
def get_db() -> Generator[Session, None, None]:
    """Get a database connection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/message")
async def reply(
    Body: str = Form(),
    From: str = Form(),
    db: Session = Depends(get_db),
) -> str:
    """Reply to a whatsapp message from the user."""
    # The generated text
    chat_response = get_response(Body)

    logger.info("Received a message from the user")
    logger.info(f"User message: {Body}")

    if chat_response is None:
        logger.error("Failed to get a response from the OpenAI API")
        return ""

    # Store the conversation in the database
    try:
        conversation = Conversation(
            sender=From,
            message=Body,
            response=chat_response,
        )
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")
    send_message(From, chat_response)
    return ""
