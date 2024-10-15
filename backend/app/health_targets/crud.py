import logging

from operator import and_, or_
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models

import health_targets.schema as health_targets_schema

# Define a loggger created on main.py
logger = logging.getLogger("myLogger")


def get_user_health_targets(
    user_id: int, db: Session
):
    try:
        # Get the health_targets from the database
        health_targets = (
            db.query(models.HealthTargets)
            .filter(models.HealthTargets.user_id == user_id)
            .first()
        )

        # Check if there are health_targets if not return None
        if not health_targets:
            return None

        # Return the health_targets
        return health_targets

    except Exception as err:
        # Log the exception
        logger.error(f"Error in get_user_health_targets: {err}", exc_info=True)
        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_health_targets(
    user_id: int, db: Session
):
    try:
        # Create a new health_target
        db_health_targets = models.HealthTargets(
            user_id=user_id,
            weight=None,
        )

        # Add the health_targets to the database
        db.add(db_health_targets)
        db.commit()
        db.refresh(db_health_targets)

        health_targets = health_targets_schema.HealthTargets(
            id = db_health_targets.id,
            user_id = user_id,
        )

        # Return the health_targets
        return health_targets
    except IntegrityError as integrity_error:
        # Rollback the transaction
        db.rollback()

        # Raise an HTTPException with a 409 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate entry error. Check if there is already an entry created for the user",
        ) from integrity_error
    except Exception as err:
        # Rollback the transaction
        db.rollback()

        # Log the exception
        logger.error(f"Error in create_health_targets: {err}", exc_info=True)
        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err