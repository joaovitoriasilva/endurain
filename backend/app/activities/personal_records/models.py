from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from core.database import Base


# Data model for personal_records table using SQLAlchemy's ORM
class PersonalRecord(Base):
    __tablename__ = "personal_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID that the PR belongs to",
    )
    activity_id = Column(
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Activity ID that set this PR",
    )
    activity_type = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Activity type (1 - run, 4 - ride, 8 - swim, 19 - strength training, etc.)",
    )
    pr_date = Column(
        DateTime,
        nullable=False,
        comment="Date when the PR was set",
    )
    metric = Column(
        String(length=100),
        nullable=False,
        index=True,
        comment="PR metric (e.g., 'fastest_5km', 'longest_distance', 'squat_1rm')",
    )
    value = Column(
        DECIMAL(precision=20, scale=10),
        nullable=False,
        comment="PR value (time in seconds, distance in meters, weight in kg, etc.)",
    )
    unit = Column(
        String(length=50),
        nullable=False,
        comment="Unit of measurement (e.g., 'seconds', 'meters', 'kg', 'watts')",
    )

    # Define a relationship to the User model
    user = relationship("User", back_populates="personal_records")

    # Define a relationship to the Activity model
    activity = relationship("Activity", back_populates="personal_records")
