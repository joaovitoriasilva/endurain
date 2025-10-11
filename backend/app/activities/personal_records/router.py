from typing import Annotated, Callable
from fastapi import APIRouter, Depends, Security, HTTPException, status

import activities.personal_records.crud as personal_records_crud
import activities.personal_records.schema as personal_records_schema
import activities.personal_records.utils as personal_records_utils

import core.database as core_database
import session.security as session_security
import users.user.dependencies as users_dependencies

from sqlalchemy.orm import Session

# Define the API router
router = APIRouter()


@router.get(
    "/user/{user_id}",
    response_model=list[personal_records_schema.PersonalRecord],
)
async def read_user_personal_records(
    user_id: int,
    validate_user_id: Annotated[Callable, Depends(users_dependencies.validate_user_id)],
    check_scopes: Annotated[
        Callable, Security(session_security.check_scopes, scopes=["activities:read"])
    ],
    db: Session = Depends(core_database.get_db),
):
    """Get all personal records for a user"""
    try:
        personal_records = personal_records_crud.get_user_personal_records(user_id, db)
        return personal_records
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


@router.post(
    "/user/{user_id}/recalculate",
    status_code=status.HTTP_200_OK,
)
async def recalculate_user_personal_records(
    user_id: int,
    validate_user_id: Annotated[Callable, Depends(users_dependencies.validate_user_id)],
    check_scopes: Annotated[
        Callable, Security(session_security.check_scopes, scopes=["activities:write"])
    ],
    db: Session = Depends(core_database.get_db),
):
    """Recalculate all personal records for a user"""
    try:
        await personal_records_utils.recalculate_all_user_prs(user_id, db)
        return {"message": "Personal records recalculated successfully"}
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err
