from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from .env import PG_DATABASE, PG_HOST, PG_PASSWORD, PG_USER

url = URL.create(
    drivername="postgresql",
    username=PG_USER,
    password=PG_PASSWORD,
    host=PG_HOST,
    database=PG_DATABASE,
    port=5432,
)

engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    message = Column(String)
    response = Column(String)


Base.metadata.create_all(engine)
