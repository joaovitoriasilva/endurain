from typing import Annotated, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes,
    APIKeyHeader,
    APIKeyCookie,
)

import session.constants as session_constants
import session.token_manager as session_token_manager

import core.logger as core_logger

# Define the OAuth2 scheme for handling bearer tokens
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes=session_constants.SCOPE_DICT,
    auto_error=False,
)

# Define the API key header for the client type
header_client_type_scheme = APIKeyHeader(name="X-Client-Type")

# Define the API key cookie for the access token
cookie_access_token_scheme = APIKeyCookie(
    name="endurain_access_token",
    auto_error=False,
)
# Define the API key cookie for the refresh token
cookie_refresh_token_scheme = APIKeyCookie(
    name="endurain_refresh_token",
    auto_error=False,
)


def get_token(
    non_cookie_token: Annotated[Union[str, None], Depends(oauth2_scheme)],
    cookie_token: Union[str, None],
    client_type: str,
    token_type: str,
) -> str:
    """
    Retrieves the authentication token based on client type and available sources.

    Args:
        non_cookie_token (str | None): Token provided via non-cookie method (e.g., Authorization header).
        cookie_token (str | None): Token provided via cookie.
        client_type (str): Type of client requesting the token ("web" or "mobile").
        token_type (str): Type of token being requested (e.g., "access", "refresh").

    Returns:
        str: The authentication token appropriate for the client type.

    Raises:
        HTTPException: If both tokens are missing, or if the client type is invalid.
    """
    if non_cookie_token is None and cookie_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{token_type.capitalize()} token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if client_type == "web":
        return cookie_token
    if client_type == "mobile":
        return non_cookie_token
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid client type",
        headers={"WWW-Authenticate": "Bearer"},
    )


## ACCESS TOKEN VALIDATION
def get_access_token(
    non_cookie_access_token: Annotated[Union[str, None], Depends(oauth2_scheme)],
    cookie_access_token: Union[str, None] = Depends(cookie_access_token_scheme),
    client_type: str = Depends(header_client_type_scheme),
) -> str:
    """
    Retrieves the access token from either the Authorization header or a cookie, depending on the client type.

    Args:
        non_cookie_access_token (str | None): Access token provided via the Authorization header (OAuth2 scheme).
        cookie_access_token (str | None): Access token provided via a cookie.
        client_type (str): The type of client making the request, extracted from a custom header.

    Returns:
        str: The resolved access token based on the client type and available sources.

    Raises:
        HTTPException: If no valid access token is found or the client type is unsupported.
    """
    return get_token(
        non_cookie_access_token, cookie_access_token, client_type, "access"
    )


def validate_access_token(
    # access_token: Annotated[str, Depends(get_access_token_from_cookies)]
    access_token: Annotated[str, Depends(get_access_token)],
    token_manager: Annotated[
        session_token_manager.TokenManager,
        Depends(session_token_manager.get_token_manager),
    ],
) -> None:
    """
    Validates the provided access token for expiration.

    This function checks whether the given access token is still valid by verifying its expiration.
    If the token is expired or invalid, an HTTPException is raised and the error is logged.
    Any unexpected errors during validation are also logged and result in a 500 Internal Server Error.

    Args:
        access_token (str): The access token to be validated.
        token_manager (session_token_manager.TokenManager): The token manager instance used for validation.

    Raises:
        HTTPException: If the token is expired, invalid, or an unexpected error occurs during validation.
    """
    try:
        # Validate the token expiration
        token_manager.validate_token_expiration(access_token)
    except HTTPException as http_err:
        core_logger.print_to_log(
            f"Access token validation failed: {http_err.detail}",
            "error",
            exc=http_err,
            context={"access_token": "[REDACTED]"},
        )
        raise
    except Exception as err:
        core_logger.print_to_log(
            f"Unexpected error during access token validation: {err}",
            "error",
            exc=err,
            context={"access_token": "[REDACTED]"},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during access token validation.",
        ) from err


def get_sub_from_access_token(
    access_token: Annotated[str, Depends(get_access_token)],
    token_manager: Annotated[
        session_token_manager.TokenManager,
        Depends(session_token_manager.get_token_manager),
    ],
) -> int:
    """
    Retrieves the user ID ('sub' claim) from the provided access token.

    Args:
        access_token (str): The access token from which to extract the claim.
        token_manager (session_token_manager.TokenManager): The token manager instance used to decode and validate the token.

    Returns:
        int: The user ID associated with the access token.

    Raises:
        Exception: If the token is invalid or the 'sub' claim is missing.
    """
    # Return the user ID associated with the token
    return token_manager.get_token_claim(access_token, "sub")


def get_sid_from_access_token(
    access_token: Annotated[str, Depends(get_access_token)],
    token_manager: Annotated[
        session_token_manager.TokenManager,
        Depends(session_token_manager.get_token_manager),
    ],
) -> int:
    """
    Retrieves the session ID ('sid') from the provided access token.

    Args:
        access_token (str): The access token from which to extract the session ID.
        token_manager (session_token_manager.TokenManager): The token manager used to validate and extract claims from the token.

    Returns:
        int: The session ID ('sid') associated with the access token.

    Raises:
        Exception: If the token is invalid or the 'sid' claim is not present.
    """
    # Return the user ID associated with the token
    return token_manager.get_token_claim(access_token, "sid")


def get_and_return_access_token(
    access_token: Annotated[str, Depends(get_access_token)],
) -> str:
    """
    Retrieves and returns the access token from the request dependencies.

    Args:
        access_token (str): The access token extracted via dependency injection.

    Returns:
        str: The access token.
    """
    # Return token
    return access_token


## REFRESH TOKEN VALIDATION
def get_refresh_token(
    non_cookie_refresh_token: Annotated[Union[str, None], Depends(oauth2_scheme)],
    cookie_refresh_token: Union[str, None] = Depends(cookie_refresh_token_scheme),
    client_type: str = Depends(header_client_type_scheme),
) -> str:
    """
    Retrieves the refresh token from either the Authorization header or a cookie, depending on the client type.

    Args:
        non_cookie_refresh_token (str | None): The refresh token provided via the Authorization header (if present).
        cookie_refresh_token (str | None): The refresh token provided via a cookie (if present).
        client_type (str): The type of client making the request, extracted from the request headers.

    Returns:
        str: The resolved refresh token based on the provided sources and client type.

    Raises:
        HTTPException: If no valid refresh token is found or the client type is invalid.
    """
    return get_token(
        non_cookie_refresh_token, cookie_refresh_token, client_type, "refresh"
    )


def validate_refresh_token(
    # access_token: Annotated[str, Depends(get_access_token_from_cookies)]
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    token_manager: Annotated[
        session_token_manager.TokenManager,
        Depends(session_token_manager.get_token_manager),
    ],
) -> None:
    """
    Validates the expiration of a refresh token using the provided token manager.

    Args:
        refresh_token (str): The refresh token to be validated, extracted via dependency injection.
        token_manager (session_token_manager.TokenManager): The token manager instance used to validate the token, injected via dependency.

    Raises:
        HTTPException: If the refresh token is expired or invalid, or if an unexpected error occurs during validation.

    Logs:
        Errors and unexpected exceptions are logged with context, including a redacted refresh token.
    """
    try:
        # Validate the token expiration
        token_manager.validate_token_expiration(refresh_token)
    except HTTPException as http_err:
        core_logger.print_to_log(
            f"Refresh token validation failed: {http_err.detail}",
            "error",
            exc=http_err,
            context={"refresh_token": "[REDACTED]"},
        )
        raise
    except Exception as err:
        core_logger.print_to_log(
            f"Unexpected error during refresh token validation: {err}",
            "error",
            exc=err,
            context={"refresh_token": "[REDACTED]"},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during refresh token validation.",
        ) from err


def get_sub_from_refresh_token(
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    token_manager: Annotated[
        session_token_manager.TokenManager,
        Depends(session_token_manager.get_token_manager),
    ],
) -> int:
    """
    Retrieves the user ID ('sub' claim) from a given refresh token.

    Args:
        refresh_token (str): The refresh token from which to extract the user ID.
        token_manager (session_token_manager.TokenManager): The token manager instance used to validate and parse the token.

    Returns:
        int: The user ID associated with the provided refresh token.

    Raises:
        Exception: If the token is invalid or the 'sub' claim is not found.
    """
    # Return the user ID associated with the token
    return token_manager.get_token_claim(refresh_token, "sub")


def get_sid_from_refresh_token(
    refresh_token: Annotated[str, Depends(get_refresh_token)],
    token_manager: Annotated[
        session_token_manager.TokenManager,
        Depends(session_token_manager.get_token_manager),
    ],
) -> str:
    """
    Retrieves the session ID ('sid') from a given refresh token.

    Args:
        refresh_token (str): The refresh token from which to extract the session ID.
        token_manager (session_token_manager.TokenManager): The token manager used to validate and extract claims from the token.

    Returns:
        str: The session ID associated with the provided refresh token.

    Raises:
        Exception: If the token is invalid or the 'sid' claim is not present.
    """
    # Return the session ID associated with the token
    return token_manager.get_token_claim(refresh_token, "sid")


def get_and_return_refresh_token(
    refresh_token: Annotated[str, Depends(get_refresh_token)],
) -> str:
    """
    Retrieves and returns the refresh token from the request dependencies.

    Args:
        refresh_token (str): The refresh token extracted via dependency injection.

    Returns:
        str: The provided refresh token.
    """
    # Return token
    return refresh_token


def check_scopes(
    access_token: Annotated[str, Depends(get_access_token)],
    token_manager: Annotated[
        session_token_manager.TokenManager,
        Depends(session_token_manager.get_token_manager),
    ],
    security_scopes: SecurityScopes,
) -> None:
    """
    Validates that the access token contains all required security scopes.

    Args:
        access_token (str): The access token extracted from the request.
        token_manager (session_token_manager.TokenManager): Instance responsible for managing and validating tokens.
        security_scopes (SecurityScopes): Required scopes for the endpoint.

    Raises:
        HTTPException: If any required scope is missing, raises 403 Forbidden with details.
        HTTPException: If an unexpected error occurs during scope validation, raises 500 Internal Server Error.

    Logs:
        Errors and exceptions are logged using core_logger for debugging and auditing purposes.
    """
    # Get the scope from the token
    scope = token_manager.get_token_claim(access_token, "scope")

    try:
        # Use set operations to find missing scope
        missing_scopes = set(security_scopes.scopes) - set(scope)
        if missing_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unauthorized Access - Missing permissions: {missing_scopes}",
                headers={
                    "WWW-Authenticate": f'Bearer scope="{security_scopes.scopes}"'
                },
            )
    except HTTPException as http_err:
        core_logger.print_to_log(
            f"Scope validation failed: {http_err}",
            "error",
            exc=http_err,
        )
        raise http_err
    except Exception as err:
        core_logger.print_to_log(
            f"Unexpected error during scope validation: {err}",
            "error",
            exc=err,
            context={"scope": scope, "required_scope": security_scopes.scopes},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during scope validation.",
        ) from err
