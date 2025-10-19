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

