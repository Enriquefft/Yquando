# ruff: noqa: B008
# Third-party imports
import openai
from fastapi import Depends, FastAPI, Form
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
from models import Conversation, SessionLocal
from env import OPENAI_API_KEY, TWILIO_NUMBER
from utils import logger, send_message

app = FastAPI()
# Set up the OpenAI API client
openai.api_key = OPENAI_API_KEY


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
    # Call the OpenAI API to generate text with GPT-3.5
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=Body,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # The generated text
    chat_response = response.choices[0].text.strip()

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
