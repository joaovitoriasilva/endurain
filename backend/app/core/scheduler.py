# from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import strava.activity_utils as strava_activity_utils
import strava.utils as strava_utils

import garmin.activity_utils as garmin_activity_utils
import garmin.health_utils as garmin_health_utils

import password_reset_tokens.utils as password_reset_tokens_utils

import core.logger as core_logger

# scheduler = BackgroundScheduler()
scheduler = AsyncIOScheduler()


def start_scheduler():
    if not scheduler.running:
        # Start the scheduler
        scheduler.start()
    
    add_scheduler_job(
        strava_utils.refresh_strava_tokens,
        "interval",
        60,
        [True],
        "refresh Strava user tokens every 60 minutes",
    )

    add_scheduler_job(
        strava_activity_utils.retrieve_strava_users_activities_for_days,
        "interval",
        60,
        [1, True],
        "retrieve last day Strava users activities",
    )

    add_scheduler_job(
        garmin_activity_utils.retrieve_garminconnect_users_activities_for_days,
        "interval",
        60,
        [1],
        "retrieve last day Garmin Connect users activities",
    )

    add_scheduler_job(
        garmin_health_utils.retrieve_garminconnect_users_bc_for_days,
        "interval",
        240,
        [1],
        "retrieve last day Garmin Connect users body composition",
    )

    add_scheduler_job(
        password_reset_tokens_utils.delete_invalid_tokens_from_db,
        "interval",
        60,
        [],
        "delete invalid password reset tokens from the database",
    )


def add_scheduler_job(func, interval, minutes, args, description):
    try:
        core_logger.print_to_log(
            f"Added scheduler job to {description} every {minutes} minutes"
        )
        scheduler.add_job(func, interval, minutes=minutes, args=args)
    except Exception as e:
        core_logger.print_to_log(
            f"Failed to add scheduler job to {description}: {str(e)}", "error"
        )


def stop_scheduler():
    scheduler.shutdown()
