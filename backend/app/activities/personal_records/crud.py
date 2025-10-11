from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

import activities.personal_records.schema as personal_records_schema
import activities.personal_records.models as personal_records_models

import core.logger as core_logger


def get_user_personal_records(user_id: int, db: Session):
    """Get all personal records for a user"""
    try:
        return (
            db.query(personal_records_models.PersonalRecord)
            .filter(personal_records_models.PersonalRecord.user_id == user_id)
            .all()
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_user_personal_records: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def get_personal_record_by_metric(
    user_id: int, activity_type: int, metric: str, db: Session
):
    """Get a specific personal record by user, activity type, and metric"""
    try:
        return (
            db.query(personal_records_models.PersonalRecord)
            .filter(
                and_(
                    personal_records_models.PersonalRecord.user_id == user_id,
                    personal_records_models.PersonalRecord.activity_type == activity_type,
                    personal_records_models.PersonalRecord.metric == metric,
                )
            )
            .first()
        )
    except Exception as err:
        core_logger.print_to_log(
            f"Error in get_personal_record_by_metric: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def create_personal_record(
    personal_record_data: personal_records_schema.PersonalRecordCreate, db: Session
):
    """Create a new personal record"""
    try:
        personal_record = personal_records_models.PersonalRecord(
            user_id=personal_record_data.user_id,
            activity_id=personal_record_data.activity_id,
            activity_type=personal_record_data.activity_type,
            pr_date=personal_record_data.pr_date,
            metric=personal_record_data.metric,
            value=personal_record_data.value,
            unit=personal_record_data.unit,
        )

        db.add(personal_record)
        db.commit()
        db.refresh(personal_record)

        return personal_record
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in create_personal_record: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def update_personal_record(
    personal_record_id: int,
    personal_record_data: personal_records_schema.PersonalRecordCreate,
    db: Session,
):
    """Update an existing personal record"""
    try:
        personal_record = (
            db.query(personal_records_models.PersonalRecord)
            .filter(personal_records_models.PersonalRecord.id == personal_record_id)
            .first()
        )

        if personal_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal record not found",
            )

        personal_record.activity_id = personal_record_data.activity_id
        personal_record.pr_date = personal_record_data.pr_date
        personal_record.value = personal_record_data.value

        db.commit()
        db.refresh(personal_record)

        return personal_record
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in update_personal_record: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err


def delete_personal_records_by_activity(activity_id: int, db: Session):
    """Delete all personal records associated with an activity"""
    try:
        db.query(personal_records_models.PersonalRecord).filter(
            personal_records_models.PersonalRecord.activity_id == activity_id
        ).delete()
        db.commit()
    except Exception as err:
        db.rollback()
        core_logger.print_to_log(
            f"Error in delete_personal_records_by_activity: {err}", "error", exc=err
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from err
