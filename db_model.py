from sqlalchemy import Enum, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, scoped_session, declarative_base
from typing import List, Optional
from sqlalchemy import create_engine
from uuid import uuid4


# Create the engine
engine = create_engine('sqlite:///db/db.sqlite3')

# Create a scoped session to manage sessions for each request
Session = scoped_session(sessionmaker(bind=engine))

# Base class for the models
Base = declarative_base()


def generate_uid() -> str:
    """
    Generates a unique identifier (UID) using the UUID4 algorithm.

    Returns:
        str: The generated unique identifier.
    """
    return str(uuid4())


class User(Base):
    """
    Represents a User entity in the database.

    Attributes:
        id (int): The primary key for the User table.
        email (str): The email address of the user.
        uploads (List[Upload]): A list of uploads associated with the user.
    """
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    uploads: Mapped[List["Upload"]] = relationship("Upload", backref='user', lazy=True, cascade='all, delete-orphan')


class Upload(Base):
    """
    Represents an Upload entity in the database.

    Attributes:
        id (int): The primary key for the Upload table.
        uid (str): The unique identifier for the upload.
        filename (str): The original filename of the uploaded file.
        upload_time (DateTime): The timestamp of when the Web API received the upload.
        finish_time (Optional[DateTime]): The timestamp of when the Explainer finished processing the upload.
        status (str): The current status of the upload (either 'pending' or 'done').
        user_id (Optional[int]): The foreign key referencing the User table, indicating the user who uploaded this upload.
    """
    __tablename__ = "upload"
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(36), default=generate_uid, nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(128), nullable=False)
    upload_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    finish_time: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(Enum("pending", "done", name="upload_status"), default="pending")
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'))


def create_all():
    """
    Creates all the tables defined in the models.

    This function should be called when setting up the application to create the necessary tables in the database.
    """
    Base.metadata.create_all(engine)
