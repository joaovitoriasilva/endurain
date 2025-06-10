from sqlalchemy import (
    Column,
    Integer,
    String,
    DATETIME,
    ForeignKey,
    Boolean,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


# Data model for gear table using SQLAlchemy's ORM
class Gear(Base):
    __tablename__ = "gear"

    id = Column(Integer, primary_key=True)
    brand = Column(
        String(length=250), nullable=True, comment="Gear brand (May include spaces)"
    )
    model = Column(
        String(length=250), nullable=True, comment="Gear model (May include spaces)"
    )
    nickname = Column(
        String(length=250),
        index=True,
        nullable=False,
        comment="Gear nickname (May include spaces)",
    )
    gear_type = Column(
        Integer, nullable=False, comment="Gear type (1 - bike, 2 - shoes, 3 - wetsuit, 4 - racquet, 5 - skis, 6 - snowboard)"
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User ID that the gear belongs to",
    )
    created_at = Column(
        DATETIME,
        nullable=False,
        default=func.now(),
        comment="Gear creation date (DATETIME)",
    )
    is_active = Column(
        Integer, nullable=False, comment="Is gear active (0 - not active, 1 - active)"
    )
    initial_kms = Column(
        DECIMAL(precision=11, scale=3),
        nullable=False,
        default=0,
        comment="Initial kilometers of the gear",
    )
    strava_gear_id = Column(
        String(length=45), unique=True, nullable=True, comment="Strava gear ID"
    )
    garminconnect_gear_id = Column(
        String(length=45), unique=True, nullable=True, comment="Garmin Connect gear ID"
    )

    # Define a relationship to the User model
    user = relationship("User", back_populates="gear")
    # Establish a one-to-many relationship with 'activities'
    activities = relationship("Activity", back_populates="gear")
    users_default_run_gear = relationship(
        "UsersDefaultGear",
        back_populates="run_gear",
        foreign_keys="[UsersDefaultGear.run_gear_id]",
    )
    users_default_trail_run_gear = relationship(
        "UsersDefaultGear",
        back_populates="trail_run_gear",
        foreign_keys="[UsersDefaultGear.trail_run_gear_id]",
    )
    users_default_virtual_run_gear = relationship(
        "UsersDefaultGear",
        back_populates="virtual_run_gear",
        foreign_keys="[UsersDefaultGear.virtual_run_gear_id]",
    )
    users_default_ride_gear = relationship(
        "UsersDefaultGear",
        back_populates="ride_gear",
        foreign_keys="[UsersDefaultGear.ride_gear_id]",
    )
    users_default_gravel_ride_gear = relationship(
        "UsersDefaultGear",
        back_populates="gravel_ride_gear",
        foreign_keys="[UsersDefaultGear.gravel_ride_gear_id]",
    )
    users_default_mtb_ride_gear = relationship(
        "UsersDefaultGear",
        back_populates="mtb_ride_gear",
        foreign_keys="[UsersDefaultGear.mtb_ride_gear_id]",
    )
    users_default_virtual_ride_gear = relationship(
        "UsersDefaultGear",
        back_populates="virtual_ride_gear",
        foreign_keys="[UsersDefaultGear.virtual_ride_gear_id]",
    )
    users_default_ows_gear = relationship(
        "UsersDefaultGear",
        back_populates="ows_gear",
        foreign_keys="[UsersDefaultGear.ows_gear_id]",
    )
    users_default_walk_gear = relationship(
        "UsersDefaultGear",
        back_populates="walk_gear",
        foreign_keys="[UsersDefaultGear.walk_gear_id]",
    )
    users_default_hike_gear = relationship(
        "UsersDefaultGear",
        back_populates="hike_gear",
        foreign_keys="[UsersDefaultGear.hike_gear_id]",
    )
    users_default_tennis_gear = relationship(
        "UsersDefaultGear",
        back_populates="tennis_gear",
        foreign_keys="[UsersDefaultGear.tennis_gear_id]",
    )
    users_default_alpine_ski_gear = relationship(
        "UsersDefaultGear",
        back_populates="alpine_ski_gear",
        foreign_keys="[UsersDefaultGear.alpine_ski_gear_id]",
    )
    users_default_nordic_ski_gear = relationship(
        "UsersDefaultGear",
        back_populates="nordic_ski_gear",
        foreign_keys="[UsersDefaultGear.nordic_ski_gear_id]",
    )
    users_default_snowboard_gear = relationship(
        "UsersDefaultGear",
        back_populates="snowboard_gear",
        foreign_keys="[UsersDefaultGear.snowboard_gear_id]",
    )
