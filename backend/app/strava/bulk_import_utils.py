import os
import csv
from fastapi import HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from stravalib.client import Client

from typing import Annotated, Callable

import core.config as core_config
import core.logger as core_logger
import core.database as core_database
import core.dependencies as core_dependencies

import users.user.crud as users_crud

import strava.utils as strava_utils
import strava.athlete_utils as strava_athlete_utils

import gears.gear.schema as gears_schema
import gears.gear.crud as gears_crud
import gears.gear.utils as gears_utils

import activities.activity.schema as activities_schema
import activities.activity.crud as activities_crud
import activities.activity.utils as activities_utils

import session.security as session_security

import users.user_integrations.crud as user_integrations_crud

from core.database import SessionLocal

import websocket.schema as websocket_schema

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Security,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

def iterate_over_activities_csv() -> dict:
    """
    Parses information in a Strava activities.csv file.

    Returns: Dictionary that contains the activities.csv file data.
    """
    # Ensure the 'strava_import' directory exists (.csv files will be here)
    strava_import_dir = core_config.STRAVA_BULK_IMPORT_DIR
    os.makedirs(strava_import_dir, exist_ok=True)

    # Build activities file path
    strava_activities_file_name = core_config.STRAVA_BULK_IMPORT_ACTIVITIES_FILE
    strava_activities_file = os.path.join(strava_import_dir, strava_activities_file_name)

    # Importing data from Strava activities file.
    # Using Python's core CSV module here - https://docs.python.org/3/library/csv.html
    if os.path.isfile(strava_activities_file):
        #core_logger.print_to_log_and_console(f"Strava {strava_activities_file_name} file present. Going to try to parse it.") #Testing code.
        try:
            strava_activities_dict = {}
            with open(strava_activities_file, newline='') as csvfile:
                strava_activities_csv = csv.DictReader(csvfile)
                # Process CSV file
                for row in strava_activities_csv:    # Must process CSV file object while file is still open.
                    # Check to see if file has headers that will be used during parsing of the file.
                    if ('Filename' not in row) or ('Activity Description' not in row) or ('Activity Gear' not in row) or ('Activity ID' not in row) or ('Media' not in row) or ('Activity Date' not in row) or ('Activity Name' not in row) or ('Activity Type' not in row):
                        core_logger.print_to_log_and_console(f"Aborting Strava bulk activities import: Proper headers not found in {strava_activities_file}.  File should have 'Filename', 'Activity Date', 'Activity Description', 'Activity Gear', 'Activity ID', 'Activity Name', 'Activity Type', and 'Media'.")
                        return None
                    _, strava_act_file_name = os.path.split(row['Filename'])  # strips path, returns filename with extension.
                    strava_activities_dict[strava_act_file_name] = row  # Store activity information in a dictionary using filename as the key
            core_logger.print_to_log_and_console(f"Strava activities csv file parsed, and it is {len(strava_activities_dict)} rows long")
            return strava_activities_dict
        except Exception as err:
            strava_activities_dict = None
            core_logger.print_to_log_and_console(f"Strava activities CSV parsing failed with error: {err}.", "error")
            return None
    else:
        core_logger.print_to_log_and_console(f"Strava activities file not found. File should be at: {strava_activities_file}")
        return None


def create_gear_dictionary_for_bulk_import(
    token_user_id: Annotated[
    int,
    Depends(session_security.get_user_id_from_access_token),
    ],
    db: Annotated[
        Session,
        Depends(core_database.get_db),
    ],
) -> dict:
    """
    Creates a dictionary that links gear nicknames in Endurain to their Endurain gear IDs. 

    The dictionary includes both base Endurain gear nickname and the gearn name smoosh ("{brand} {model} {name}") that Strava uses for its shoe gear listing in activities.csv

    Returns: Dictionary that uses the gear name as a key to look up the gear ID.
    """
    user = users_crud.get_user_by_id(token_user_id, db)
    user_gear_list = gears_crud.get_gear_user(user.id, db)
    if user_gear_list is None:
            #User has no gear.
            users_existing_gear_nickname_to_id = None
    else:
            #User has gear - build dictionary to facilitate gear to ID work during import.
            users_existing_gear_nickname_to_id = {}
            for item in user_gear_list:
                users_existing_gear_nickname_to_id[item.nickname] = [item.id]
                # Strava apparently exports shoe names as a smoosh of "{brand} {model} {name}", so adding that as a second key for each gear item
                strava_name_smoosh = item.brand + " " + item.model + " " + item.nickname
                if strava_name_smoosh not in users_existing_gear_nickname_to_id:
                        users_existing_gear_nickname_to_id[strava_name_smoosh] = [item.id]
    return users_existing_gear_nickname_to_id

def queue_bulk_export_activities_for_import(
    token_user_id: Annotated[
    int,
    Depends(session_security.get_user_id_from_access_token),
    ],
    websocket_manager: Annotated[
        websocket_schema.WebSocketManager,
        Depends(websocket_schema.get_websocket_manager),
    ],
    db: Annotated[
        Session,
        Depends(core_database.get_db),
    ],
    strava_activities_dict: dict, 
    users_existing_gear_nickname_to_id: dict,
    import_time: str, 
    background_tasks: BackgroundTasks,
) -> int:
    """
    Queues files located in the Strava bulk import activities directory for processing.

    Returns: Number of files that were queued.
    """
    # Function to queue files for importing from a Strava bulk export. 
    # Returns the number of files to process, for log messages.

    # Ensure the 'strava_import/activities' directory exists (activity files will be here)
    strava_activities_import_dir = core_config.STRAVA_BULK_IMPORT_ACTIVITIES_DIR
    os.makedirs(strava_activities_import_dir, exist_ok=True)

    # Ensure the 'strava_import/media' directory exists (media files will be here)
    strava_media_import_dir = core_config.STRAVA_BULK_IMPORT_MEDIA_DIR
    os.makedirs(strava_media_import_dir, exist_ok=True)

    # Grab list of supported file formats
    supported_file_formats = core_config.SUPPORTED_FILE_FORMATS

    # Get file list of all files in the 'strava_import/activities' directory
    filelist = os.listdir(strava_activities_import_dir)

    # Get total file count and log it
    totalfilecount=len(filelist)
    core_logger.print_to_log_and_console(f"Found {totalfilecount} files in the {strava_activities_import_dir}.")

    # Build a list of importable files
    skippedprocessingcount=0
    importable_files = []
    for filename in filelist:
        file_path = os.path.join(strava_activities_import_dir, filename)

        # Check if file is one we can process
        _, file_extension = os.path.splitext(file_path)
        if file_extension not in supported_file_formats:
            core_logger.print_to_log_and_console(f"Skipping file {file_path} - due to not having a supported file extension. Supported extensions are: {supported_file_formats}.")
            skippedprocessingcount+=1
            continue
        else:
            importable_files.append(filename)

    # Check if there are any importable files and log status
    number_of_importable_files = len(importable_files)
    if number_of_importable_files == 0: 
        core_logger.print_to_log_and_console(f"There are no importable files in {strava_activities_import_dir} directory - aborting import.", "warning")
        return 0
    core_logger.print_to_log_and_console(f"Skipped a total of {skippedprocessingcount} files due to not having a supported file extension. There are now {number_of_importable_files} files to queue for processing. ")

    # Iterate over each importable file and queue import
    filenumber=0
    queuedforprocessingcount=0
    for filename in importable_files:
        filenumber+=1
        file_path = os.path.join(strava_activities_import_dir, filename)

        if os.path.isfile(file_path):
            core_logger.print_to_log_and_console(f"Queuing file number {filenumber} for processing: {file_path}")
            # Build dictionary for import progress status reporting in logs
            file_progress_dict = {'filenumber': filenumber, 'totalfilecount': number_of_importable_files }
            # Parse and store the activity
            background_tasks.add_task(
                activities_utils.parse_and_store_activity_from_file,
                token_user_id,
                file_path,
                websocket_manager,
                db,
                strava_activities=strava_activities_dict,
                import_initiated_time=import_time,
                users_existing_gear_nickname_to_id=users_existing_gear_nickname_to_id,
                file_progress_dict=file_progress_dict,
            )
            queuedforprocessingcount+=1
    
    return queuedforprocessingcount
