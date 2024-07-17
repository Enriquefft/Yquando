"""Main API module for the chatbot."""

# ruff: noqa: B008
from typing import Generator

from fastapi import Depends, FastAPI, Form
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ai import get_response

# Internal imports
from models import Crop, Farm, SessionLocal, User
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
    """Reply to a WhatsApp message from the user."""
    phone_number = From.removeprefix("whatsapp:")

    user = db.query(User).filter(User.phone_number == phone_number).first()

    if not user:
        if "register" in Body.lower():
            return await register_user(Body, phone_number, db)
        else:  # noqa: RET505
            send_message(
                From,
                "You are not registered. To register, please start your message with 'register' followed by your details in this format:\n\n"
                "'register, Name, Location, Crop1:Size1;Crop2:Size2;...'\n\n"
                "Example: 'register, John Doe, Valley Farms, Corn:50;Wheat:30;Soybeans:20'\n\n"
                "Please ensure to provide all the details accurately.",
            )
            return ""

    farm = user.farm
    crop_info = [{"name": crop.name, "size": crop.size} for crop in farm.crops]

    # Detailed system message for the AI
    system_message = (
        f"User {user.name} has a farm at {farm.location}. "
        f"The following crops are cultivated on this farm:\n"
    )

    for crop in crop_info:
        system_message += f"- {crop['name']}: {crop['size']} acres\n"

    system_message += (
        "\nConsidering the location, crop size, and crop type, provide detailed recommendations on "
        "the frequency and quantity of watering for each crop. Take into account local weather conditions, "
        "soil type, crop growth stage, and any other relevant factors. Use the following format for each crop:\n"
        "\nCrop Name:\n"
        "- Watering Frequency: [e.g., daily, weekly]\n"
        "- Watering Quantity: [e.g., liters per acre]\n"
        "- Additional Notes: [e.g., water more during dry spells]\n"
    )

    chat_response = get_response(
        Body,
        system_message=system_message,
    )

    logger.info("Received a message from the user")
    logger.info(f"User message: {Body}")

    if chat_response is None:
        logger.error("Failed to get a response from the chat system")
        return ""

    send_message(From, chat_response)
    return ""


async def register_user(body: str, phone_number: str, db: Session) -> str:
    """Register a new user."""
    try:
        details = body.split(",")
        if len(details) != 4:
            return "Please provide all details in the format: register, Name, Location, Crop1:Size1;Crop2:Size2;..."

        _, name, location, crops = details

        user = User(
            name=name.strip(),
            phone_number=phone_number,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        farm = Farm(location=location.strip(), owner_id=user.id)
        db.add(farm)
        db.commit()
        db.refresh(farm)

        crop_list = crops.split(
            ";"
        )  # Assuming crops are provided as a semicolon-separated string
        for crop in crop_list:
            crop_name, crop_size = crop.split(":")
            crop_size = float(crop_size)
            new_crop = Crop(name=crop_name.strip(), size=crop_size, farm_id=farm.id)
            db.add(new_crop)

        db.commit()
        send_message(f"whatsapp:{phone_number}", "Registration successful.")
        return "Registration successful."
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error registering user: {e}")
        return "Registration failed. Please try again."
