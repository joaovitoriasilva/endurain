"""
Script to migrate existing activities and calculate personal records.
This can be run as a one-time migration or scheduled as a background task.

Usage:
    python -m activities.personal_records.migration
"""

import asyncio
from sqlalchemy.orm import Session

import core.database as core_database
import core.logger as core_logger
import users.user.crud as users_crud
import activities.personal_records.utils as personal_records_utils


async def migrate_all_users_prs():
    """
    Migrate all users' activities to calculate personal records.
    This is a one-time migration that should be run after the PR feature is deployed.
    """
    db = next(core_database.get_db())
    
    try:
        # Get all users
        users = users_crud.get_all_users(db)
        
        if not users:
            core_logger.print_to_log("No users found")
            return
        
        core_logger.print_to_log(f"Starting PR migration for {len(users)} users")
        
        for user in users:
            try:
                core_logger.print_to_log(f"Calculating PRs for user {user.id} ({user.username})")
                await personal_records_utils.recalculate_all_user_prs(user.id, db)
                core_logger.print_to_log(f"Completed PRs for user {user.id}")
            except Exception as err:
                core_logger.print_to_log(
                    f"Error calculating PRs for user {user.id}: {err}", 
                    "error", 
                    exc=err
                )
                continue
        
        core_logger.print_to_log("PR migration completed for all users")
        
    except Exception as err:
        core_logger.print_to_log(
            f"Error in migrate_all_users_prs: {err}", 
            "error", 
            exc=err
        )
        raise
    finally:
        db.close()


async def migrate_single_user_prs(user_id: int):
    """
    Migrate a single user's activities to calculate personal records.
    
    Args:
        user_id: The ID of the user to migrate
    """
    db = next(core_database.get_db())
    
    try:
        core_logger.print_to_log(f"Calculating PRs for user {user_id}")
        await personal_records_utils.recalculate_all_user_prs(user_id, db)
        core_logger.print_to_log(f"Completed PRs for user {user_id}")
    except Exception as err:
        core_logger.print_to_log(
            f"Error calculating PRs for user {user_id}: {err}", 
            "error", 
            exc=err
        )
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Run the migration
    import sys
    
    if len(sys.argv) > 1:
        # Migrate specific user
        user_id = int(sys.argv[1])
        asyncio.run(migrate_single_user_prs(user_id))
    else:
        # Migrate all users
        asyncio.run(migrate_all_users_prs())
