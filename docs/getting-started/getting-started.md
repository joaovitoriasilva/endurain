# Getting started

---

Welcome to the guide for getting started on hosting your own production instance of Endurain. Like many other services, Endurain is easiest to get up and running trough Docker compose. It is possible to get Endurain up and running without a domain and reverse proxy, but this guide assumes you want to use a reverse proxy and your domain. Endurain can run on any computer that support OCI containers, but in this guide we are using Debian 13 (should also work with 12).

## Prerequisites
* Domain name pointed to your external IP address.
* Open FW rules to your server on port 443 and 80. (trough NAT if you are running ipv4)
* A computer/server with enough disk space for your activity files.
* API key from [geocode.maps.co](https://geocode.maps.co/) (free, but need to register).

## Installing docker and Caddy reverse proxy

We use apt to do this

```
sudo apt update -y
sudo apt install docker.io docker-compose caddy -y
```

Confirm your user has the id 1000:

```
id
```

If you are not the user 1000, you need to set the `UID` and `GID` to your id in the .env file. But to keep this guide as easy to follow as possible, we will assume that you are user 1000.

## Create directory structure

Lets use `/opt/endurain/` as the root directory for our project.

```bash
sudo mkdir /opt/endurain
sudo chown 1000:1000 /opt/endurain
mkdir -p \
  /opt/endurain/app/{data,logs} \
  /opt/endurain/postgres
```

## Docker compose Deployment

In this example of setting up Endurain, we will need two files. One `docker-compose.yml` and `.env`.

* docker-compose.yml tells your system how to set up the container, network and storage.
* .env holds our secrets and environment variables.

Splitting up the setup like this make it easy to handle updates to the containers, without touching the secrets and other variables.

### Creating the docker-compose and .env file

To make it as easy as possible for selfhoster to get up and running examples of docker-compose.yml and .env is on the git repo. Here are links to the files on the repo:

* [docker-compose.yml.example](https://raw.githubusercontent.com/joaovitoriasilva/endurain/refs/heads/master/docker-compose.yml.example)
* [.env.example](https://raw.githubusercontent.com/joaovitoriasilva/endurain/refs/heads/master/.env.example)

```bash
cd /opt/endurain
wget https://raw.githubusercontent.com/joaovitoriasilva/endurain/refs/heads/master/docker-compose.yml.example
wget https://raw.githubusercontent.com/joaovitoriasilva/endurain/refs/heads/master/.env.example

mv docker-compose.yml.example docker-compose.yml
mv .env.example .env
```

Now we need to make changes to the files to reflect *your* environment. Inside docker-compose.yml there is not much we need to do. If you want to store the files another place then `/opt/endurain` this is the file you need to change.

Here is an explaination on what you can set in the `.env`:

Environment variable  | How to set it |
| --- | --- |
| DB_PASSWORD | Run `openssl rand -hex 32` on a terminal to get a secret |
| POSTGRES_PASSWORD | Set the same value as DB_PASSWORD.|
| SECRET_KEY | Run `openssl rand -hex 32` on a terminal to get a secret |
| FERNET_KEY |Run `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` on a terminal to get a secret or go to [https://fernetkeygen.com](https://fernetkeygen.com). Example output is `7NfMMRSCWcoNDSjqBX8WoYH9nTFk1VdQOdZY13po53Y=` |
| GEOCODES_MAPS_API | <a href="https://geocode.maps.co/">Geocode maps</a> offers a free plan consisting of 1 Request/Second. Registration necessary. |
| TZ | Timezone definition. Insert your timezone. List of available time zones [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). Format `Europe/Lisbon` expected |
| ENDURAIN_HOST | https://endurain.yourdomain.com |
| BEHIND_PROXY | Change to true if behind reverse proxy |
| POSTGRES_DB | Postgres name for the database. |
| POSTGRES_USER | Postgres user for the database. |

**Please note:**

POSTGRES_DB and POSTGRES_USER is values for the database. If you change it from endurain, you also need to set the environment variables for the app image. Please leave them as `endurain` if you are unsure.

### Start the stack

It is finally time to start the stack!

```bash
cd /opt/endurain
sudo docker compose up -d
```

Check the log output:

```
docker compose logs -f
```

If you do not get any errors, continue to next step.

### Visit the site

* Visit the site insecurly on http://`IP-OF-YOUR-SERVER`:8080
* We still can not login to the site, because the `ENDURAIN_HOST` doesn't match our local URL.

##  Configure Caddy as reverse proxy and get SSL cert from letsencrypt

* Before we configure caddy you need to set your DNS provider to point your domain to your external IP.
* You also need to open your firewall on port 443 and 80 to the server.

We use caddy outside docker. This way Debian handles the updates (you just need to run `sudo apt get update -y` and `sudo apt get upgrade -y`)

Caddy is configured in the file `/etc/caddy/Caddyfile`

Open the file in your favourite editor, delete the default text, and paste in this:

```
endurain.yourdomain.com {
        reverse_proxy localhost:8080
}
```

Restart caddy

```
sudo systemctl restart caddy
```

Check the ouput of caddy with:

```
sudo journalctl -u caddy
```

You should now be able to access your site on endurain.yourdomain.com

**Log in with username: admin password: admin, and remember to change the password**



🎉 **Weee** 🎉 You now have your own instance of Endurain up and running!

## How to update

* Take a backup of your files and db.
* Check for new releases of the container image [here](https://github.com/joaovitoriasilva/endurain). Read release notes carefully for breaking changes.
* Log on your server and run:
* Inside `/opt/endurain/docker-compose.yml`, change out the version tag (the version after `:`)


```bash
cd /opt/endurain
sudo docker compose pull
sudo docker compose up -d
```

The same is the case for Postgres. Check for breaking changes in release notes on [Postgres Website](https://www.postgresql.org/docs/release/).

** It is generally pretty safe to upgrade postgres minor version f.eks 17.4 to 17.5, but major is often breaking change (example 17.2 to 18.1 )


## Things to think about

You should implement backup strategy for the following directories:

```
/opt/endurain/app/data
/opt/endurain/app/logs
```

You also need to backup your postgres database. It is not good practice to just backup the volume `/opt/endurain/postgres` this might be corrupted if  the database is in the middle of a wright when the database goes down.

## Default Credentials

- **Username:** admin  
- **Password:** admin
