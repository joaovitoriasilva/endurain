from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from core.database import Base


class UsersSessions(Base):
    """
    Represents a user session in the system.

    Attributes:
        id (str): Unique identifier for the session (UUID).
        user_id (int): ID of the user to whom the session belongs.
        refresh_token (str): Hashed refresh token for the session.
        ip_address (str): IP address of the client initiating the session.
        device_type (str): Type of device used for the session.
        operating_system (str): Operating system of the device.
        operating_system_version (str): Version of the operating system.
        browser (str): Browser used for the session.
        browser_version (str): Version of the browser.
        created_at (datetime): Timestamp when the session was created.
        expires_at (datetime): Timestamp when the session expires.
        user (User): Relationship to the User model.
    """
    __tablename__ = "users_sessions"

    id = Column(String(length=36), nullable=False, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID that the session belongs",
    )
    refresh_token = Column(
        String(length=255), nullable=False, comment="Session hashed refresh token"
    )
    ip_address = Column(String(45), nullable=False, comment="Client IP address")
    device_type = Column(String(length=45), nullable=False, comment="Device type")
    operating_system = Column(
        String(length=45), nullable=False, comment="Operating system"
    )
    operating_system_version = Column(
        String(length=45), nullable=False, comment="Operating system version"
    )
    browser = Column(String(length=45), nullable=False, comment="Browser")
    browser_version = Column(
        String(length=45), nullable=False, comment="Browser version"
    )
    created_at = Column(
        DateTime, nullable=False, comment="Session creation date (datetime)"
    )
    expires_at = Column(
        DateTime, nullable=False, comment="Session expiration date (datetime)"
    )

    # Define a relationship to the User model
    user = relationship("User", back_populates="users_sessions")
