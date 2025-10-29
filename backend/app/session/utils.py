"""Session utility functions and classes"""

from enum import Enum
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from fastapi import (
    Request,
)
from user_agents import parse

from sqlalchemy.orm import Session

import auth.constants as auth_constants
import session.schema as session_schema
import session.crud as session_crud
import auth.password_hasher as auth_password_hasher

import users.user.schema as users_schema


class DeviceType(Enum):
    """
    An enumeration representing different types of devices.

    Attributes:
        MOBILE: Represents a mobile device.
        TABLET: Represents a tablet device.
        PC: Represents a personal computer/desktop device.
    """

    MOBILE = "Mobile"
    TABLET = "Tablet"
    PC = "PC"


@dataclass
class DeviceInfo:
    """
    Represents information about a user's device.

    Attributes:
        device_type (DeviceType): The type of device (e.g., mobile, desktop).
        operating_system (str): The name of the operating system (e.g., 'Windows', 'macOS').
        operating_system_version (str): The version of the operating system.
        browser (str): The name of the browser (e.g., 'Chrome', 'Firefox').
        browser_version (str): The version of the browser.
    """

    device_type: DeviceType
    operating_system: str
    operating_system_version: str
    browser: str
    browser_version: str


def create_session_object(
    session_id: str,
    user: users_schema.UserRead,
    request: Request,
    hashed_refresh_token: str,
    refresh_token_exp: datetime,
) -> session_schema.UsersSessions:
    """
    Creates a UsersSessions object representing a user session with device and request metadata.

    Args:
        session_id (str): Unique identifier for the session.
        user (users_schema.UserRead): The user associated with the session.
        request (Request): The HTTP request object containing client information.
        hashed_refresh_token (str): The hashed refresh token for the session.
        refresh_token_exp (datetime): The expiration datetime for the refresh token.

    Returns:
        session_schema.UsersSessions: The session object populated with user, device, and request details.
    """
    user_agent = get_user_agent(request)
    device_info = parse_user_agent(user_agent)

    return session_schema.UsersSessions(
        id=session_id,
        user_id=user.id,
        refresh_token=hashed_refresh_token,
        ip_address=get_ip_address(request),
        device_type=device_info.device_type.value,
        operating_system=device_info.operating_system,
        operating_system_version=device_info.operating_system_version,
        browser=device_info.browser,
        browser_version=device_info.browser_version,
        created_at=datetime.now(timezone.utc),
        expires_at=refresh_token_exp,
    )


def edit_session_object(
    request: Request,
    hashed_refresh_token: str,
    refresh_token_exp: datetime,
    session: Session,
) -> session_schema.UsersSessions:
    """
    Edits and returns a UsersSessions object with updated session information.

    Args:
        request (Request): The incoming HTTP request object.
        hashed_refresh_token (str): The hashed refresh token to associate with the session.
        refresh_token_exp (datetime): The expiration datetime for the refresh token.
        session (Session): The existing session object to update.

    Returns:
        session_schema.UsersSessions: The updated UsersSessions object containing session details such as device info, IP address, and token expiration.
    """
    user_agent = get_user_agent(request)
    device_info = parse_user_agent(user_agent)

    return session_schema.UsersSessions(
        id=session.id,
        user_id=session.user_id,
        refresh_token=hashed_refresh_token,
        ip_address=get_ip_address(request),
        device_type=device_info.device_type.value,
        operating_system=device_info.operating_system,
        operating_system_version=device_info.operating_system_version,
        browser=device_info.browser,
        browser_version=device_info.browser_version,
        created_at=session.created_at,
        expires_at=refresh_token_exp,
    )


def create_session(
    session_id: str,
    user: users_schema.UserRead,
    request: Request,
    refresh_token: str,
    password_hasher: auth_password_hasher.PasswordHasher,
    db: Session,
) -> None:
    """
    Creates a new user session and stores it in the database.

    Args:
        session_id (str): Unique identifier for the session.
        user (users_schema.UserRead): The user for whom the session is being created.
        request (Request): The incoming HTTP request object.
        refresh_token (str): The refresh token to be associated with the session.
        password_hasher (auth_password_hasher.PasswordHasher): Utility to hash the refresh token.
        db (Session): Database session for storing the session.

    Returns:
        None
    """
    # Calculate the refresh token expiration date
    exp = datetime.now(timezone.utc) + timedelta(
        days=auth_constants.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    # Create a new session
    new_session = create_session_object(
        session_id,
        user,
        request,
        password_hasher.hash_password(refresh_token),
        exp,
    )

    # Add the session to the database
    session_crud.create_session(new_session, db)


def edit_session(
    session: session_schema.UsersSessions,
    request: Request,
    new_refresh_token: str,
    password_hasher: auth_password_hasher.PasswordHasher,
    db: Session,
) -> None:
    """
    Edits an existing user session by updating its refresh token and expiration date.

    Args:
        session (session_schema.UsersSessions): The current user session object to be edited.
        request (Request): The incoming request object containing session context.
        new_refresh_token (str): The new refresh token to be set for the session.
        password_hasher (auth_password_hasher.PasswordHasher): Utility for hashing the refresh token.
        db (Session): Database session for committing changes.

    Returns:
        None
    """
    # Calculate the refresh token expiration date
    exp = datetime.now(timezone.utc) + timedelta(
        days=auth_constants.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    # Update the session
    updated_session = edit_session_object(
        request,
        password_hasher.hash_password(new_refresh_token),
        exp,
        session,
    )

    # Update the session in the database
    session_crud.edit_session(updated_session, db)


def get_user_agent(request: Request) -> str:
    """
    Extracts the 'User-Agent' string from the request headers.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        str: The value of the 'User-Agent' header if present, otherwise an empty string.
    """
    return request.headers.get("user-agent", "")


def get_ip_address(request: Request) -> str:
    """
    Extracts the client's IP address from a FastAPI Request object.

    This function checks for common proxy headers ("X-Forwarded-For" and "X-Real-IP") to determine the original client IP address.
    If these headers are not present, it falls back to the direct client host information.

    Args:
        request (Request): The FastAPI Request object containing headers and client info.

    Returns:
        str: The determined IP address of the client, or "unknown" if it cannot be determined.
    """
    # Check for proxy headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


def parse_user_agent(user_agent: str) -> DeviceInfo:
    """
    Parse a user agent string and extract device information.

    This function analyzes a user agent string to determine device characteristics
    including device type, operating system, and browser information.

    Args:
        user_agent (str): The user agent string to parse.

    Returns:
        DeviceInfo: An object containing parsed device information with the following attributes:
            - device_type: The type of device (MOBILE, TABLET, or PC)
            - operating_system: The name of the operating system family
            - operating_system_version: The version string of the operating system
            - browser: The name of the browser family
            - browser_version: The version string of the browser

    Note:
        - Device type is determined based on whether the user agent indicates a mobile
          or tablet device, defaulting to PC if neither.
        - If any information cannot be determined, it defaults to "Unknown".
    """
    ua = parse(user_agent)
    device_type = (
        DeviceType.MOBILE
        if ua.is_mobile
        else DeviceType.TABLET if ua.is_tablet else DeviceType.PC
    )

    return DeviceInfo(
        device_type=device_type,
        operating_system=ua.os.family or "Unknown",
        operating_system_version=ua.os.version_string or "Unknown",
        browser=ua.browser.family or "Unknown",
        browser_version=ua.browser.version_string or "Unknown",
    )
