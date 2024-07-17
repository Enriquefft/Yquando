"""Module for database models and session creation."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from env import PG_DATABASE, PG_HOST, PG_PASSWORD, PG_USER

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


class User(Base):
    """Model for user table."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String)

    farm = relationship("Farm", uselist=False, back_populates="owner")


class Farm(Base):
    """Model for farm table."""

    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="farm")
    crops = relationship("Crop", back_populates="farm")


class Crop(Base):
    """Model for crop table."""

    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    size = Column(Float)
    farm_id = Column(Integer, ForeignKey("farms.id"))

    farm = relationship("Farm", back_populates="crops")


Base.metadata.create_all(engine)
