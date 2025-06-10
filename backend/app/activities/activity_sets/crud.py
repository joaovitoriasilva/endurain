from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import activities.activity.models as activity_models
import activities.activity.crud as activity_crud

import activities.activity_sets.models as activity_sets_models
import activities.activity_sets.schema as activity_sets_schema
import activities.activity_sets.utils as activity_sets_utils

import server_settings.crud as server_settings_crud

import core.logger as core_logger


def get_activity_sets(activity_id: int, token_user_id: int, db: Session):
    try:
        activity = activity_crud.get_activity_by_id(
            activity_id, db
        )

        if not activity:
            # If the activity does not exist, return None
            return None

        user_is_owner = True
        if token_user_id != activity.user_id:
            user_is_owner = False

        if not user_is_owner and activity.hide_workout_sets_steps:
            # If the user is not the owner and sets/steps are hidden, return None
            return None
        
        # Get the activity sets from the database
        activity_sets = (
            db.query(activity_sets_models.ActivitySets)
            .filter(
                activity_sets_models.ActivitySets.activity_id == activity_id,
            )
            .all()
        )

        # Check if there are activity sets if not return None
        if not activity_sets:
            return None

        # Serialize the activity sets
        for set in activity_sets:
            set = activity_sets_utils.serialize_activity_set(activity, set)

        # Return the activity sets
        return activity_sets
    except Exception as err:
        # Log the exception
        core_logger.print_to_log(f"Error in get_activity_sets: {err}", "error", exc=err)
        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_public_activity_sets(activity_id: int, db: Session):
    try:
        activity = activity_crud.get_activity_by_id(
            activity_id, db
        )

        if not activity:
            # If the activity does not exist, return None
            return None
        
        if activity.hide_workout_sets_steps:
            # If the sets/steps are hidden, return None
            return None
        
        # Check if public sharable links are enabled in server settings
        server_settings = server_settings_crud.get_server_settings(db)

        # Return None if public sharable links are disabled
        if not server_settings or not server_settings.public_shareable_links:
            return None

        # Get the activity sets from the database
        activity_sets = (
            db.query(activity_sets_models.ActivitySets)
            .join(
                activity_models.Activity,
                activity_models.Activity.id
                == activity_sets_models.ActivitySets.activity_id,
            )
            .filter(
                activity_sets_models.ActivitySets.activity_id == activity_id,
                activity_models.Activity.visibility == 0,
                activity_models.Activity.id == activity_id,
            )
            .all()
        )

        # Check if there are activity sets, if not return None
        if not activity_sets:
            return None

        # Serialize the activity sets
        for set in activity_sets:
            set = activity_sets_utils.serialize_activity_set(activity, set)

        # Return the activity sets
        return activity_sets
    except Exception as err:
        # Log the exception
        core_logger.print_to_log(
            f"Error in get_public_activity_sets: {err}", "error", exc=err
        )
        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_activity_sets(
    activity_sets: list[activity_sets_schema.ActivitySets],
    activity_id: int,
    db: Session,
):
    try:
        # Create a list to store the ActivitySets objects
        sets = []

        # Iterate over the list of ActivitySets objects
        for set in activity_sets:
            # Create an ActivitySets object
            db_stream = activity_sets_models.ActivitySets(
                activity_id=activity_id,
                duration=set[0],
                repetitions=set[1],
                weight=set[2],
                set_type=set[3],
                start_time=set[4],
                category=set[5][0] if set[5] else None,
                category_subtype=(
                    set[6][0] if set[6] else None
                ),
            )

            # Append the object to the list
            sets.append(db_stream)

        # Bulk insert the list of ActivitySets objects
        db.bulk_save_objects(sets)
        db.commit()
    except Exception as err:
        # Rollback the transaction
        db.rollback()

        # Log the exception
        core_logger(f"Error in create_activity_sets: {err}", "error", exc=err)
        # Raise an HTTPException with a 500 Internal Server Error status code
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err
