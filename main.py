# ruff: noqa: B008
# Third-party imports
from fastapi import Depends, FastAPI, Form
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
from models import Conversation, SessionLocal
from env import TWILIO_NUMBER
from utils import logger, send_message

from ai import get_response

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"msg": "up & running"}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/message")
async def reply(Body: str = Form(), db: Session = Depends(get_db)):
    # The generated text
    chat_response = get_response(Body)

    if chat_response is None:
        logger.error("Failed to get a response from the OpenAI API")
        return ""

    # Store the conversation in the database
    try:
        conversation = Conversation(
            sender=TWILIO_NUMBER,
            message=Body,
            response=chat_response,
        )
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")
    send_message(TWILIO_NUMBER, chat_response)
    return ""
