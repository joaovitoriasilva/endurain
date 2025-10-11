from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

import activities.activity.crud as activities_crud
import activities.activity.schema as activities_schema
import activities.personal_records.crud as personal_records_crud
import activities.personal_records.schema as personal_records_schema

import core.logger as core_logger

# Activity type categories
RUNNING_TYPES = [1, 2, 3, 34]  # Run, Trail run, Virtual run, Track run
CYCLING_TYPES = [4, 5, 6, 7, 27, 28, 29, 35, 36]  # Various bike types
SWIMMING_TYPES = [8, 9]  # Lap swimming, Open water swimming
STRENGTH_TYPES = [19, 20]  # Strength training, Crossfit


def check_and_update_personal_records(
    activity: activities_schema.Activity, db: Session
) -> list:
    """
    Check if an activity sets any new personal records and update the database.
    Returns a list of new PRs that were set.
    """
    new_prs = []

    try:
        if activity.activity_type in RUNNING_TYPES:
            new_prs.extend(_check_running_prs(activity, db))
        elif activity.activity_type in CYCLING_TYPES:
            new_prs.extend(_check_cycling_prs(activity, db))
        elif activity.activity_type in SWIMMING_TYPES:
            new_prs.extend(_check_swimming_prs(activity, db))
        elif activity.activity_type in STRENGTH_TYPES:
            new_prs.extend(_check_strength_prs(activity, db))

        return new_prs
    except Exception as err:
        core_logger.print_to_log(
            f"Error in check_and_update_personal_records: {err}", "error", exc=err
        )
        return []


def _check_running_prs(activity: activities_schema.Activity, db: Session) -> list:
    """Check for running personal records"""
    new_prs = []

    if not activity.distance or not activity.total_elapsed_time:
        return new_prs

    distance_meters = activity.distance
    time_seconds = float(activity.total_elapsed_time)

    # Define distance milestones in meters
    milestones = {
        "fastest_1km": 1000,
        "fastest_5km": 5000,
        "fastest_10km": 10000,
        "fastest_half_marathon": 21097,
        "fastest_marathon": 42195,
    }

    # Check if activity distance matches milestone (within 2% tolerance)
    for metric, milestone_distance in milestones.items():
        distance_diff = abs(distance_meters - milestone_distance)
        tolerance = milestone_distance * 0.02  # 2% tolerance
        
        if distance_diff <= tolerance:
            # Activity distance is close enough to milestone
            pr_time = time_seconds

            # Check existing PR
            existing_pr = personal_records_crud.get_personal_record_by_metric(
                activity.user_id, activity.activity_type, metric, db
            )

            is_new_pr = False
            if existing_pr is None:
                is_new_pr = True
            elif float(existing_pr.value) > pr_time:
                is_new_pr = True

            if is_new_pr:
                pr_data = personal_records_schema.PersonalRecordCreate(
                    user_id=activity.user_id,
                    activity_id=activity.id,
                    activity_type=activity.activity_type,
                    pr_date=activity.start_time,
                    metric=metric,
                    value=Decimal(str(pr_time)),
                    unit="seconds",
                )

                if existing_pr:
                    personal_records_crud.update_personal_record(
                        existing_pr.id, pr_data, db
                    )
                else:
                    personal_records_crud.create_personal_record(pr_data, db)

                new_prs.append(metric)

    # Check longest distance
    existing_longest = personal_records_crud.get_personal_record_by_metric(
        activity.user_id, activity.activity_type, "longest_distance", db
    )

    if existing_longest is None or float(existing_longest.value) < distance_meters:
        pr_data = personal_records_schema.PersonalRecordCreate(
            user_id=activity.user_id,
            activity_id=activity.id,
            activity_type=activity.activity_type,
            pr_date=activity.start_time,
            metric="longest_distance",
            value=Decimal(str(distance_meters)),
            unit="meters",
        )

        if existing_longest:
            personal_records_crud.update_personal_record(
                existing_longest.id, pr_data, db
            )
        else:
            personal_records_crud.create_personal_record(pr_data, db)

        new_prs.append("longest_distance")

    # Check best average pace (lower is better)
    if activity.pace:
        pace_value = float(activity.pace)
        existing_pace = personal_records_crud.get_personal_record_by_metric(
            activity.user_id, activity.activity_type, "best_average_pace", db
        )

        if existing_pace is None or float(existing_pace.value) > pace_value:
            pr_data = personal_records_schema.PersonalRecordCreate(
                user_id=activity.user_id,
                activity_id=activity.id,
                activity_type=activity.activity_type,
                pr_date=activity.start_time,
                metric="best_average_pace",
                value=Decimal(str(pace_value)),
                unit="seconds_per_meter",
            )

            if existing_pace:
                personal_records_crud.update_personal_record(
                    existing_pace.id, pr_data, db
                )
            else:
                personal_records_crud.create_personal_record(pr_data, db)

            new_prs.append("best_average_pace")

    return new_prs


def _check_cycling_prs(activity: activities_schema.Activity, db: Session) -> list:
    """Check for cycling personal records"""
    new_prs = []

    if not activity.distance or not activity.total_elapsed_time:
        return new_prs

    distance_meters = activity.distance
    time_seconds = float(activity.total_elapsed_time)

    # Define distance milestones in meters
    milestones = {
        "fastest_5km": 5000,
        "fastest_20km": 20000,
        "fastest_40km": 40000,
    }

    # Check if activity distance matches milestone (within 2% tolerance)
    for metric, milestone_distance in milestones.items():
        distance_diff = abs(distance_meters - milestone_distance)
        tolerance = milestone_distance * 0.02  # 2% tolerance
        
        if distance_diff <= tolerance:
            pr_time = time_seconds

            existing_pr = personal_records_crud.get_personal_record_by_metric(
                activity.user_id, activity.activity_type, metric, db
            )

            is_new_pr = False
            if existing_pr is None:
                is_new_pr = True
            elif float(existing_pr.value) > pr_time:
                is_new_pr = True

            if is_new_pr:
                pr_data = personal_records_schema.PersonalRecordCreate(
                    user_id=activity.user_id,
                    activity_id=activity.id,
                    activity_type=activity.activity_type,
                    pr_date=activity.start_time,
                    metric=metric,
                    value=Decimal(str(pr_time)),
                    unit="seconds",
                )

                if existing_pr:
                    personal_records_crud.update_personal_record(
                        existing_pr.id, pr_data, db
                    )
                else:
                    personal_records_crud.create_personal_record(pr_data, db)

                new_prs.append(metric)

    # Check longest distance
    existing_longest = personal_records_crud.get_personal_record_by_metric(
        activity.user_id, activity.activity_type, "longest_distance", db
    )

    if existing_longest is None or float(existing_longest.value) < distance_meters:
        pr_data = personal_records_schema.PersonalRecordCreate(
            user_id=activity.user_id,
            activity_id=activity.id,
            activity_type=activity.activity_type,
            pr_date=activity.start_time,
            metric="longest_distance",
            value=Decimal(str(distance_meters)),
            unit="meters",
        )

        if existing_longest:
            personal_records_crud.update_personal_record(
                existing_longest.id, pr_data, db
            )
        else:
            personal_records_crud.create_personal_record(pr_data, db)

        new_prs.append("longest_distance")

    # Check power metrics
    if activity.max_power:
        existing_max_power = personal_records_crud.get_personal_record_by_metric(
            activity.user_id, activity.activity_type, "max_power", db
        )

        if existing_max_power is None or float(existing_max_power.value) < activity.max_power:
            pr_data = personal_records_schema.PersonalRecordCreate(
                user_id=activity.user_id,
                activity_id=activity.id,
                activity_type=activity.activity_type,
                pr_date=activity.start_time,
                metric="max_power",
                value=Decimal(str(activity.max_power)),
                unit="watts",
            )

            if existing_max_power:
                personal_records_crud.update_personal_record(
                    existing_max_power.id, pr_data, db
                )
            else:
                personal_records_crud.create_personal_record(pr_data, db)

            new_prs.append("max_power")

    if activity.normalized_power:
        existing_np = personal_records_crud.get_personal_record_by_metric(
            activity.user_id, activity.activity_type, "best_normalized_power", db
        )

        if existing_np is None or float(existing_np.value) < activity.normalized_power:
            pr_data = personal_records_schema.PersonalRecordCreate(
                user_id=activity.user_id,
                activity_id=activity.id,
                activity_type=activity.activity_type,
                pr_date=activity.start_time,
                metric="best_normalized_power",
                value=Decimal(str(activity.normalized_power)),
                unit="watts",
            )

            if existing_np:
                personal_records_crud.update_personal_record(
                    existing_np.id, pr_data, db
                )
            else:
                personal_records_crud.create_personal_record(pr_data, db)

            new_prs.append("best_normalized_power")

    return new_prs


def _check_swimming_prs(activity: activities_schema.Activity, db: Session) -> list:
    """Check for swimming personal records"""
    new_prs = []

    if not activity.distance or not activity.total_elapsed_time:
        return new_prs

    distance_meters = activity.distance
    time_seconds = float(activity.total_elapsed_time)

    # Define distance milestones in meters
    milestones = {
        "fastest_50m": 50,
        "fastest_100m": 100,
        "fastest_200m": 200,
        "fastest_400m": 400,
        "fastest_1500m": 1500,
    }

    # Check if activity distance matches milestone (within 5% tolerance for swimming)
    for metric, milestone_distance in milestones.items():
        distance_diff = abs(distance_meters - milestone_distance)
        tolerance = milestone_distance * 0.05  # 5% tolerance (pools can vary)
        
        if distance_diff <= tolerance:
            pr_time = time_seconds

            existing_pr = personal_records_crud.get_personal_record_by_metric(
                activity.user_id, activity.activity_type, metric, db
            )

            is_new_pr = False
            if existing_pr is None:
                is_new_pr = True
            elif float(existing_pr.value) > pr_time:
                is_new_pr = True

            if is_new_pr:
                pr_data = personal_records_schema.PersonalRecordCreate(
                    user_id=activity.user_id,
                    activity_id=activity.id,
                    activity_type=activity.activity_type,
                    pr_date=activity.start_time,
                    metric=metric,
                    value=Decimal(str(pr_time)),
                    unit="seconds",
                )

                if existing_pr:
                    personal_records_crud.update_personal_record(
                        existing_pr.id, pr_data, db
                    )
                else:
                    personal_records_crud.create_personal_record(pr_data, db)

                new_prs.append(metric)

    # Check longest distance
    existing_longest = personal_records_crud.get_personal_record_by_metric(
        activity.user_id, activity.activity_type, "longest_distance", db
    )

    if existing_longest is None or float(existing_longest.value) < distance_meters:
        pr_data = personal_records_schema.PersonalRecordCreate(
            user_id=activity.user_id,
            activity_id=activity.id,
            activity_type=activity.activity_type,
            pr_date=activity.start_time,
            metric="longest_distance",
            value=Decimal(str(distance_meters)),
            unit="meters",
        )

        if existing_longest:
            personal_records_crud.update_personal_record(
                existing_longest.id, pr_data, db
            )
        else:
            personal_records_crud.create_personal_record(pr_data, db)

        new_prs.append("longest_distance")

    return new_prs


def _check_strength_prs(activity: activities_schema.Activity, db: Session) -> list:
    """
    Check for strength training personal records.
    Note: This is a placeholder. Full implementation would require activity_sets data
    to track specific exercises and weights.
    """
    new_prs = []
    # Strength training PRs would require analyzing activity_sets
    # This is beyond the scope of basic implementation
    # Future enhancement: Parse activity_sets to find max weights for specific exercises
    return new_prs


async def recalculate_all_user_prs(user_id: int, db: Session):
    """
    Recalculate all personal records for a user from scratch.
    This is useful for initial data load or fixing inconsistencies.
    """
    try:
        # Get all activities for the user, ordered by date
        activities = activities_crud.get_user_activities(user_id, db)

        if not activities:
            return

        # Delete all existing PRs for the user
        db.query(personal_records_crud.personal_records_models.PersonalRecord).filter(
            personal_records_crud.personal_records_models.PersonalRecord.user_id == user_id
        ).delete()
        db.commit()

        # Process each activity chronologically
        for activity in activities:
            check_and_update_personal_records(activity, db)

        core_logger.print_to_log(
            f"Recalculated all PRs for user {user_id}"
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in recalculate_all_user_prs: {err}", "error", exc=err
        )
        raise
