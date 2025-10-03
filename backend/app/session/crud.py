"""CRUD operations for user sessions."""

from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import session.models as session_models
import session.schema as session_schema

import core.logger as core_logger


class SessionNotFoundError(Exception):
    """
    Exception raised when a requested session cannot be found.

    This error is typically used to indicate that an operation requiring a session
    failed because the session does not exist in the data store.

    Attributes:
        message (str): Optional explanation of the error.
    """


def get_user_sessions(
    user_id: int, db: Session
) -> list[session_models.UsersSessions] | None:
    """
    Retrieve all session records for a given user, ordered by creation date descending.

    Args:
        user_id (int): The ID of the user whose sessions are to be retrieved.
        db (Session): SQLAlchemy database session.

    Returns:
        list[session_models.UsersSessions]: List of session objects for the user, ordered by most recent.
        None: If no sessions are found for the user.

    Raises:
        HTTPException: If an error occurs during retrieval, raises a 500 Internal Server Error.
    """
    try:
        db_sessions = (
            db.query(session_models.UsersSessions)
            .filter(session_models.UsersSessions.user_id == user_id)
            .order_by(session_models.UsersSessions.created_at.desc())
            .all()
        )

        # If the no session was found, return None
        if db_sessions is None:
            return None

        # Return the sessions
        return db_sessions
    except Exception as err:
        # Log the exception
        core_logger.print_to_log(f"Error in get_user_sessions: {err}", "error", exc=err)

        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions",
        ) from err


def get_session_by_refresh_token(
    refresh_token: str, db: Session
) -> session_models.UsersSessions | None:
    """
    Retrieve a user session from the database using a refresh token, ensuring the session is not expired.

    Args:
        refresh_token (str): The refresh token associated with the user session.
        db (Session): The SQLAlchemy database session.

    Returns:
        UsersSessions | None: The user session object if found and not expired, otherwise None.

    Raises:
        HTTPException: If an error occurs during retrieval, raises a 500 Internal Server Error.
    """
    try:
        # Get the session from the database, ensure it's not expired
        db_session = (
            db.query(session_models.UsersSessions)
            .filter(session_models.UsersSessions.refresh_token == refresh_token)
            .filter(
                session_models.UsersSessions.expires_at > datetime.now(timezone.utc)
            )
            .first()
        )

        # Return the session
        return db_session
    except Exception as err:
        # Log the exception
        core_logger.print_to_log(
            f"Error in get_session_by_refresh_token: {err}", "error", exc=err
        )

        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session",
        ) from err


def create_session(
    session: session_schema.UsersSessions, db: Session
) -> session_models.UsersSessions:
    """
    Creates a new user session in the database.

    Args:
        session (session_schema.UsersSessions): The session data to be created.
        db (Session): The SQLAlchemy database session.

    Returns:
        session_models.UsersSessions: The newly created session object.

    Raises:
        HTTPException: If an error occurs during session creation, raises a 500 Internal Server Error.
    """
    try:
        # Create a new session using model_dump
        db_session = session_models.UsersSessions(**session.model_dump())

        # Add the session to the database
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        # Return the session
        return db_session
    except Exception as err:
        # Rollback the transaction
        db.rollback()

        # Log the exception
        core_logger.print_to_log(f"Error in create_session: {err}", "error", exc=err)

        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session",
        ) from err


def edit_session(session: session_schema.UsersSessions, db: Session) -> None:
    """
    Edits an existing user session in the database.

    This function retrieves a session by its ID, updates its fields with the provided values,
    and commits the changes to the database. If the session does not exist, it raises a 404 error.
    If any other exception occurs, it rolls back the transaction, logs the error, and raises a 500 error.

    Args:
        session (session_schema.UsersSessions): The session data containing updated fields.
        db (Session): The SQLAlchemy database session.

    Raises:
        HTTPException: If the session is not found (404) or if an error occurs during update (500).
    """
    try:
        # Get the session from the database
        db_session = (
            db.query(session_models.UsersSessions)
            .filter(session_models.UsersSessions.id == session.id)
            .first()
        )

        # Check if the session exists, if not raises exception
        if not db_session:
            raise SessionNotFoundError(f"Session {session.id} not found")

        # Dictionary of the fields to update if they are not None
        session_data = session.model_dump(exclude_unset=True)
        # Iterate over the fields and update the db_session dynamically
        for key, value in session_data.items():
            setattr(db_session, key, value)

        # Commit the transaction
        db.commit()
    except SessionNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except Exception as err:
        # Rollback the transaction
        db.rollback()

        # Log the exception
        core_logger.print_to_log(f"Error in edit_session: {err}", "error", exc=err)

        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session",
        ) from err


def delete_session(session_id: str, user_id: int, db: Session) -> None:
    """
    Deletes a user session from the database.

    Args:
        session_id (str): The unique identifier of the session to delete.
        user_id (int): The ID of the user associated with the session.
        db (Session): The SQLAlchemy database session.

    Raises:
        HTTPException: If the session is not found (404) or if an error occurs during deletion (500).

    Notes:
        - Rolls back the transaction and logs the error if an unexpected exception occurs.
        - Commits the transaction if the session is successfully deleted.
    """
    try:
        # Delete the session
        num_deleted = (
            db.query(session_models.UsersSessions)
            .filter(
                session_models.UsersSessions.id == session_id,
                session_models.UsersSessions.user_id == user_id,
            )
            .delete()
        )

        # Check if the session was found and deleted
        if num_deleted == 0:
            raise SessionNotFoundError(
                f"Session {session_id} not found for user {user_id}"
            )

        # Commit the transaction
        db.commit()
    except SessionNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except Exception as err:
        # Rollback the transaction
        db.rollback()

        # Log the exception
        core_logger.print_to_log(f"Error in delete_session: {err}", "error", exc=err)

        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session",
        ) from err
