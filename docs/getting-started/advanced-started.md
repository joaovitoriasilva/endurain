## Default Credentials

- **Username:** admin  
- **Password:** admin

## Docker Deployment

Endurain provides a Docker image for simplified deployment. To get started, check out the `docker-compose.yml.example` file in the project repository and adjust it according to your setup. Supported tags are:

- **latest:** contains the latest released version;
- **version, example "v0.3.0":** contains the app state available at the time of the version specified;
- **development version, example "dev_06092024":** contains a development version of the app at the date specified. This is not a stable released and may contain issues and bugs. Please do not open issues if using a version like this unless asked by me.

## Supported Environment Variables
Table below shows supported environment variables. Variables marked with optional "No" should be set to avoid errors.

| Environment variable  | Default value | Optional | Notes |
| --- | --- | --- | --- |
| UID | 1000 | Yes | User ID for mounted volumes. Default is 1000 |
| GID | 1000 | Yes | Group ID for mounted volumes. Default is 1000 |
| TZ | UTC | Yes | Timezone definition. Useful for TZ calculation for activities that do not have coordinates associated, like indoor swim or weight training. If not specified UTC will be used. List of available time zones [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). Format `Europe/Lisbon` expected |
| ENDURAIN_HOST | No default set | `No` | Required for internal communication and Strava. For Strava https must be used. Host or local ip (example: http://192.168.1.10:8080 or https://endurain.com) |
| REVERSE_GEO_PROVIDER | nominatim | Yes | Defines reverse geo provider. Expects <a href="https://geocode.maps.co/">geocode</a>, photon or nominatim. photon can be the <a href="https://photon.komoot.io">SaaS by komoot</a> or a self hosted version like a <a href="https://github.com/rtuszik/photon-docker">self hosted version</a>. Like photon, Nominatim can be the <a href="https://nominatim.openstreetmap.org/">SaaS</a> or a self hosted version |
| PHOTON_API_HOST | photon.komoot.io | Yes | API host for photon. By default it uses the <a href="https://photon.komoot.io">SaaS by komoot</a> |
| PHOTON_API_USE_HTTPS | true | Yes | Protocol used by photon. By default uses HTTPS to be inline with what <a href="https://photon.komoot.io">SaaS by komoot</a> expects |
| NOMINATIM_API_HOST | nominatim.openstreetmap.org | Yes | API host for Nominatim. By default it uses the <a href="https://nominatim.openstreetmap.org">SaaS</a> |
| NOMINATIM_API_USE_HTTPS | true | Yes | Protocol used by Nominatim. By default uses HTTPS to be inline with what <a href="https://nominatim.openstreetmap.org">SaaS</a> expects |
| GEOCODES_MAPS_API | changeme | Yes | <a href="https://geocode.maps.co/">Geocode maps</a> offers a free plan consisting of 1 Request/Second. Registration necessary. |
| REVERSE_GEO_RATE_LIMIT | 1 | Yes | Change this if you have a paid Geocode maps tier. Other providers also use this variable. Keep it as is if you use photon or Nominatim to keep 1 request per second | 
| DB_TYPE | postgres | Yes | mariadb or postgres |
| DB_HOST | postgres | Yes | mariadb or postgres |
| DB_PORT | 5432 | Yes | 3306 or 5432 |
| DB_USER | endurain | Yes | N/A |
| DB_PASSWORD | No default set | `No` | N/A |
| DB_DATABASE | endurain | Yes | N/A |
| SECRET_KEY | No default set | `No` | Run `openssl rand -hex 32` on a terminal to get a secret |
| FERNET_KEY | No default set | `No` | Run `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` on a terminal to get a secret or go to [https://fernetkeygen.com](https://fernetkeygen.com). Example output is `7NfMMRSCWcoNDSjqBX8WoYH9nTFk1VdQOdZY13po53Y=` |
| ALGORITHM | HS256 | Yes | Currently only HS256 is supported |
| ACCESS_TOKEN_EXPIRE_MINUTES | 15 | Yes | Time in minutes |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | Yes | Time in days |
| JAEGER_ENABLED | false | Yes | N/A |
| JAEGER_PROTOCOL | http | Yes | N/A |
| JAEGER_HOST | jaeger | Yes | N/A |
| JAEGER_PORT | 4317 | Yes | N/A |
| BEHIND_PROXY | false | Yes | Change to true if behind reverse proxy |
| ENVIRONMENT | production | Yes | "production" and "development" allowed. "development" allows connections from localhost:8080 and localhost:5173 at the CORS level |
| SMTP_HOST | No default set | Yes | The SMTP host of your email provider. Example `smtp.protonmail.ch` |
| SMTP_PORT | 587 | Yes | The SMTP port of your email provider. Default is 587 |
| SMTP_USERNAME | No default set | Yes | The username of your SMTP email provider, probably your email address |
| SMTP_PASSWORD | No default set | Yes | The password of your SMTP email provider. Some providers allow the use of your account password, others require the creation of an app password. Please refer to your provider documentation |
| SMTP_SECURE | true | Yes | By default it uses secure communications. Accepted values are `true` and `false` |
| SMTP_SECURE_TYPE | starttls | Yes | If SMTP_SECURE is set you can set the communication type. Accepted values are `starttls` and `ssl` |

Table below shows the obligatory environment variables for mariadb container. You should set them based on what was also set for the Endurain container.

| Environemnt variable  | Default value | Optional | Notes |
| --- | --- | --- | --- |
| MYSQL_ROOT_PASSWORD | changeme | `No` | N/A |
| MYSQL_DATABASE | endurain | `No` | N/A |
| MYSQL_USER | endurain | `No` | N/A |
| MYSQL_PASSWORD | changeme | `No` | N/A |

Table below shows the obligatory environment variables for postgres container. You should set them based on what was also set for the Endurain container.

| Environemnt variable  | Default value | Optional | Notes |
| --- | --- | --- | --- |
| POSTGRES_PASSWORD | changeme | `No` | N/A |
| POSTGRES_DB | endurain | `No` | N/A |
| POSTGRES_USER | endurain | `No` | N/A |
| PGDATA | /var/lib/postgresql/data/pgdata | `No` | N/A |

To check Python backend dependencies used, use poetry file (pyproject.toml).

Frontend dependencies:

- To check npm dependencies used, use npm file (package.json)
- Logo created on Canva

## Volumes

Docker image uses a non-root user, so ensure target folders are not owned by root. Non-root user should use UID and GID 1000. It is recommended to configure the following volumes for data persistence:

| Volume | Notes |
| --- | --- |
| `<local_path>/endurain/backend/logs:/app/backend/logs` | Log files for the backend |
| `<local_path>/endurain/backend/data:/app/backend/data` | Necessary for image and activity files persistence on docker image update |

## Image personalization

It is possible (v0.10.0 or higher) to personalize the login image in the login page. To do that, map the data/server_images directory for image persistence on container updates and:
 - Set the image in the server settings zone of the settings page
 - A square image is expected. Default one uses 1000px vs 1000px

## Generic bulk import and file upload

To perform a bulk import:
- Place .fit, .tcx, .gz and/or .gpx files into the data/activity_files/bulk_import folder. Create the folder if needed.
- In the "Settings" menu select "Import".
- Click "Import" next to "Bulk Import".

.fit files are preferred. I noticed that Strava/Garmin Connect process of converting .fit to .gpx introduces additional data to the activity file leading to minor variances in the data, like for example additional 
meters in distance and elevation gain. Some notes:

- After the files are processed, the files are moved to the processed folder
- GEOCODES API has a limit of 1 Request/Second on the free plan, so if you have a large number of files, it might not be possible to import all in the same action
- The generic bulk import currently only imports data present in the .fit, .tcx or .gpx files - no metadata or other media are imported.

## Importing data from a Strava bulk export (BETA)

Strava allows users to create a bulk export of their historical activity on the site.  This information is stored in a zip file, primarily as .csv files, GPS recording files (e.g., .gpx, .fit), and media files (e.g., .jpg, .png).

All Strava bulk import functions expect files in the data/strava_import folder. Create the folder if needed.

Recommended procedure
1. Read the instructions below, including notes on limitations and known issues.
2. Backup your database and other core files.  There is currently no mechanism to roll-back or undo a bulk import.
3. Import, or manually create, any gear that was present in Strava.
4. Import activities and media that were in Strava.

### Importing gear from a Strava bulk export

Importing of bikes and shoes is currently possible. Bike and shoe imports are screened for duplicates via nickname, so pre-existing gear with the same nickname will prevent import of that item of gear (case-insensitively).

#### Bikes import

At the present time, importing bikes from a Strava bulk export is implemented as a beta feature - use with caution.  Components of bikes are not imported - just the bikes themselves. 

To perform an import of bikes: 
- Place the bikes.csv file from a Strava bulk export into the data/strava_import folder. Create the folder if needed.
- In the "Settings" menu select "Import".
- Click "Bikes Import" next to "Strava gear import".
- Status messages about the import, including why any gear was not imported, can be found in the logs.

Ensure the file is named "bikes.csv" and has a header row with at least the fields 'Bike Name', 'Bike Brand', and 'Bike Model'.

Note that Endurain does not allow the "+" character in gear field names, and thus all +'s will be replaced with spaces.

#### Shoe import

At the present time, importing shoes from a Strava bulk export is implemented as a beta feature - use with caution.  Components of shooes are not imported - just the shoes themselves. 

To perform an import of shoes: 
- Place the shoes.csv file from a Strava bulk export into the data/strava_import folder. Create the folder if needed.
- In the "Settings" menu select "Import".
- Click "Shoes import" next to "Strava import".
- Status messages about the import, including why any gear was not imported, can be found in the logs.

Ensure the file is named "shoes.csv" and has a header row with at least the fields 'Shoe Name', 'Shoe Brand', and 'Shoe Model'.

Note that Endurain does not allow the "+" character in gear field names, and thus all +'s will be replaced with spaces.

#### Notes on importing gear

NOTE: There is currently no mechanism to undo a gear import.

All gear will be imported as active, as Strava does not export the active/inactive status of the gear.

Note that Endurain does not allow the "+" character in gear field names, and thus all +'s will be replaced with spaces on import.

Endurain does not allow duplicate gear nicknames, regardless of case (e.g., "Ilves" and "ilves" would not be allowed). Gear with duplicate nicknames will not be imported (i.e., only the first item with a given nickname will be imported).

The import routine checks for duplicate items, and should not import duplicates. Thus it should be safe to re-import the same file mulitple times. However, due to the renaming of un-named shoes, repeated imports of the same shoe file will create duplicate entries of any unnamed shoes present. 

Gear that is already present in Endurain due to having an active link with Strava will not be imported via the manual import process.

### Importing activities and media from a Strava bulk export

At the present time, importing activities and media from a Strava bulk export is implemented as a very early beta feature - use with extreme caution. 

**We advise backing up your database, or using a test install, before importing data.  There is currently no mechanism to undo or revert an import.**

To perform an import of activities and media: 
- Place the extracted contents of a Strava bulk export .zip file in the data/strava_import folder. Create the folder if needed. 
- Consider performing a test import before attempting to import a large set of files; see notes below on how to do this.
- If you want imported activities to be linked to gear (bikes or shoes), ensure that any bikes or shoes referred to in activities are already present in Endurain. 
- In the "Settings" menu select "Import".
- Click "Strava bulk import" next to "Strava bulk activity import".
- Status messages about the import, including progress messages and why any activities or media were not imported, can be found in the logs.

In addition to the base activity track and statistics, the Strava bulk import feature should also import each activity's title, description, activity type, gear (if it exists already in Endurain), Strava activity ID (into a database field), and media. 

The structure of files expected is:
- an activities.csv file in the data/strava_import folder (required)
- activities files in the data/strava_import/activities folder (required)
- media files in the data/strava_import/media folder (optional, if you want media imported)

The activities.csv file requires a header row with at least the following fields: 'Filename', 'Activity Description', 'Activity Gear', 'Activity ID', and 'Media'.

You may import as many or as few activities as you want by placing only the activity files you want imported into the data/strava_import/activities. The importer looks for importable (i.e., .gpx, .fit, etc.) files in the activities folder and only then looks to see if each file has importable metadata and/or media present in the activities.csv file.

Thus, to perform a test import:
- Place only a few activity files into the data/strava_import/activities folder.
- Place the full activities.csv, bikes.csv, shoes.csv, and media folder contents into their respective locations. 
- Perform an import as directed, above.
- Check the logs to watch the import progress and understand the results.  

#### Strava bulk import limitations 

**The Endurain website will likely be unresponsive while the import proceeds** (fields on pages requiring database calls will not load). Logs (and the console) are updated as each file is processed; watching the logs will let you see how quickly files are being processed. 

**We advise backing up your database, or using a test Endurain install, before importing data: There is currently no mechanism to undo or revert an import.**

The bulk import of Strava activities and media does not create gear.  Please import, or create, any gear referred to in the activities before importing the activities. Ensure the nickname and other details of the gear matche precisely.

Comments associated with media are not imported (Endurain does not currently allow comments on media). FYI: Comments associated with media are stored in Strava's media.csv file.

