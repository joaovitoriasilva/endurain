from sqlalchemy.orm import Session
from sqlalchemy import text

import activities.activity.crud as activities_crud
import activities.activity.utils as activities_utils
import users.user.crud as users_crud

import core.logger as core_logger
import migrations.crud as migrations_crud


def process_migration_6(db: Session):
    core_logger.print_to_log_and_console("Started migration 6 - Adding TSS support")

    migration_successful = True

    try:
        # Add TSS column to activities table
        core_logger.print_to_log_and_console("Adding TSS column to activities table")
        db.execute(text("ALTER TABLE activities ADD COLUMN tss INTEGER NULL COMMENT 'Training Stress Score (TSS) for the activity'"))

        # Add threshold fields to users table
        core_logger.print_to_log_and_console("Adding threshold fields to users table")
        db.execute(text("ALTER TABLE users ADD COLUMN ftp INTEGER NULL COMMENT 'Functional Threshold Power (FTP) in watts for TSS calculation'"))
        db.execute(text("ALTER TABLE users ADD COLUMN lthr INTEGER NULL COMMENT 'Lactate Threshold Heart Rate (LTHR) in bpm for hrTSS calculation'"))
        db.execute(text("ALTER TABLE users ADD COLUMN run_threshold_pace DECIMAL(20,10) NULL COMMENT 'Running threshold pace in seconds per meter for rTSS calculation'"))
        db.execute(text("ALTER TABLE users ADD COLUMN swim_threshold_pace DECIMAL(20,10) NULL COMMENT 'Swimming threshold pace in seconds per meter for sTSS calculation'"))

        # Commit schema changes
        db.commit()
        core_logger.print_to_log_and_console("Database schema updated successfully")

        # Now calculate TSS for existing activities
        core_logger.print_to_log_and_console("Calculating TSS for existing activities")
        
        # Get all activities
        activities = activities_crud.get_all_activities(db)
        
        if activities:
            activities_processed = 0
            activities_with_tss = 0
            
            for activity in activities:
                try:
                    # Skip if TSS already calculated
                    if activity.tss is not None:
                        continue
                    
                    # Get user to access threshold values
                    user = users_crud.get_user_by_id(activity.user_id, db)
                    if not user:
                        continue
                    
                    # Calculate TSS using the new function
                    tss_value = activities_utils.calculate_activity_tss(
                        activity,
                        user_ftp=user.ftp,
                        user_lthr=user.lthr,
                        user_run_threshold_pace=user.run_threshold_pace,
                        user_swim_threshold_pace=user.swim_threshold_pace
                    )
                    
                    # Update activity with TSS if we calculated a value > 0
                    if tss_value > 0:
                        activity.tss = tss_value
                        activities_crud.edit_activity(activity.user_id, activity, db)
                        activities_with_tss += 1
                    
                    activities_processed += 1
                    
                    if activities_processed % 100 == 0:
                        core_logger.print_to_log_and_console(f"Processed {activities_processed} activities, {activities_with_tss} with TSS calculated")
                
                except Exception as err:
                    core_logger.print_to_log_and_console(
                        f"Migration 6 - Error calculating TSS for activity {activity.id}: {err}",
                        "warning",
                        exc=err,
                    )
                    # Continue with other activities, don't fail the entire migration
                    continue
            
            core_logger.print_to_log_and_console(f"TSS calculation complete: {activities_processed} activities processed, {activities_with_tss} with TSS values")

        # Mark migration as executed
        migrations_crud.set_migration_as_executed(6, db)
        core_logger.print_to_log_and_console("Migration 6 marked as executed")

    except Exception as err:
        core_logger.print_to_log_and_console(
            f"Migration 6 - Critical error during migration: {err}",
            "error",
            exc=err,
        )
        migration_successful = False
        db.rollback()

    if migration_successful:
        core_logger.print_to_log_and_console("Migration 6 completed successfully")
    else:
        core_logger.print_to_log_and_console("Migration 6 failed - will retry later", "error")