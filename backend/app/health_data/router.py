import logging

from typing import Annotated, Callable

from fastapi import APIRouter, Depends, UploadFile, Security, HTTPException, status
from sqlalchemy.orm import Session

import health_data.schema as health_data_schema
import health_data.crud as health_data_crud

import session.security as session_security

import core.database as core_database
import core.dependencies as core_dependencies

# Define the API router
router = APIRouter()


@router.get(
    "/number",
    response_model=int,
)
async def read_health_data_number(
    _check_scope: Annotated[
        Callable, Security(session_security.check_scope, scopes=["health:read"])
    ],
    token_user_id: Annotated[
        int,
        Depends(session_security.get_user_id_from_access_token),
    ],
    db: Annotated[
        Session,
        Depends(core_database.get_db),
    ],
):
    # Get the health_data number from the database
    return health_data_crud.get_health_data_number(token_user_id, db)


@router.get(
    "",
    response_model=list[health_data_schema.HealthData] | None,
)
async def read_health_data_all(
    _check_scope: Annotated[
        Callable, Security(session_security.check_scope, scopes=["health:read"])
    ],
    token_user_id: Annotated[
        int,
        Depends(session_security.get_user_id_from_access_token),
    ],
    db: Annotated[
        Session,
        Depends(core_database.get_db),
    ],
):
    # Get the health_data from the database
    return health_data_crud.get_all_health_data_by_user_id(token_user_id, db)


@router.get(
    "/page_number/{page_number}/num_records/{num_records}",
    response_model=list[health_data_schema.HealthData] | None,
)
async def read_health_data_all_pagination(
    page_number: int,
    num_records: int,
    _check_scope: Annotated[
        Callable, Security(session_security.check_scope, scopes=["health:read"])
    ],
    validate_pagination_values: Annotated[
        Callable, Depends(core_dependencies.validate_pagination_values)
    ],
    token_user_id: Annotated[
        int,
        Depends(session_security.get_user_id_from_access_token),
    ],
    db: Annotated[
        Session,
        Depends(core_database.get_db),
    ],
):
    # Get the health_data from the database with pagination
    return health_data_crud.get_health_data_with_pagination(
        token_user_id, db, page_number, num_records
    )


@router.post("", status_code=201)
async def create_health_data(
    health_data: health_data_schema.HealthData,
    _check_scope: Annotated[
        Callable, Security(session_security.check_scope, scopes=["health:write"])
    ],
    token_user_id: Annotated[
        int,
        Depends(session_security.get_user_id_from_access_token),
    ],
    db: Annotated[
        Session,
        Depends(core_database.get_db),
    ],
):
    # Check if health_data for this date already exists
    health_for_date = health_data_crud.get_health_data_by_date(
        token_user_id, health_data.date, db
    )

    if health_for_date:
        health_data.id = health_for_date.id
        # Updates the health_data in the database and returns it
        return health_data_crud.edit_health_data(token_user_id, health_data, db)
    else:
        # Creates the health_data in the database and returns it
        return health_data_crud.create_health_data(token_user_id, health_data, db)


@router.put("")
async def edit_health_data(
    health_data: health_data_schema.HealthData,
    _check_scope: Annotated[
        Callable, Security(session_security.check_scope, scopes=["health:write"])
    ],
    token_user_id: Annotated[
        int,
        Depends(session_security.get_user_id_from_access_token),
    ],
    db: Annotated[
        Session,
        Depends(core_database.get_db),
    ],
):
    # Updates the health_data in the database and returns it
    return health_data_crud.edit_health_data(token_user_id, health_data, db)


@router.delete("/{health_data_id}")
async def delete_health_data(
    health_data_id: int,
    _check_scope: Annotated[
        Callable, Security(session_security.check_scope, scopes=["health:write"])
    ],
    token_user_id: Annotated[
        int,
        Depends(session_security.get_user_id_from_access_token),
    ],
    db: Annotated[
        Session,
        Depends(core_database.get_db),
    ],
):
    # Deletes entry from database
    return health_data_crud.delete_health_data(token_user_id, health_data_id, db)
