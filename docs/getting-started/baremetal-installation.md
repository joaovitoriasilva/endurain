# Bare Metal Installation

---

This guide will walk you through installing Endurain directly on a Linux server without using Docker. This method gives you more control over the installation but requires manual setup of all components.

## Prerequisites

* A Linux server (Debian 12+, Ubuntu 22.04+, or similar)
* Domain name pointed to your server's IP address (optional but recommended)
* Root or sudo access
* At least 2GB of RAM and sufficient disk space for activity files
* Open firewall rules on ports 80 and 443 (if using a reverse proxy)

## System Requirements

* **Python:** 3.12 or higher
* **Node.js:** 18 or higher
* **Database:** PostgreSQL 13+ or MariaDB 10.6+
* **Reverse Proxy:** Nginx or Caddy (recommended for production)

## Installation Steps

### 1. Install System Dependencies

First, update your system and install required dependencies:

**For Debian/Ubuntu:**

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip \
  nodejs npm postgresql postgresql-contrib \
  git curl build-essential python3-dev \
  libpq-dev pkg-config
```

**For systems using MariaDB instead of PostgreSQL:**

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip \
  nodejs npm mariadb-server mariadb-client \
  git curl build-essential python3-dev \
  libmariadb-dev pkg-config
```

### 2. Install Poetry

Poetry is used to manage Python dependencies for the backend:

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

Verify the installation:

```bash
poetry --version
```

### 3. Create Application User

Create a dedicated user for running Endurain:

```bash
sudo useradd -r -m -d /opt/endurain -s /bin/bash endurain
sudo mkdir -p /opt/endurain
sudo chown endurain:endurain /opt/endurain
```

### 4. Setup Database

#### For PostgreSQL:

```bash
sudo -u postgres psql
```

Inside the PostgreSQL shell:

```sql
CREATE DATABASE endurain;
CREATE USER endurain WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE endurain TO endurain;
\q
```

#### For MariaDB:

```bash
sudo mysql
```

Inside the MariaDB shell:

```sql
CREATE DATABASE endurain CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'endurain'@'localhost' IDENTIFIED BY 'your_secure_password_here';
GRANT ALL PRIVILEGES ON endurain.* TO 'endurain'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Clone the Repository

Switch to the endurain user and clone the repository:

```bash
sudo su - endurain
cd /opt/endurain
git clone https://github.com/joaovitoriasilva/endurain.git .
```

### 6. Setup Backend

Navigate to the backend directory and install dependencies:

```bash
cd /opt/endurain/backend
poetry install --no-root
```

Create the backend data directories:

```bash
mkdir -p /opt/endurain/backend/app/data/{activity_files,activity_media,server_images,user_images}
mkdir -p /opt/endurain/backend/app/logs
```

Create environment configuration file:

```bash
cd /opt/endurain/backend
nano .env
```

Add the following content (adjust values as needed):

```env
# Timezone
TZ=UTC

# Application Settings
ENDURAIN_HOST=https://endurain.yourdomain.com
BEHIND_PROXY=true
ENVIRONMENT=production

# Database Configuration (PostgreSQL)
DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_USER=endurain
DB_PASSWORD=your_secure_password_here
DB_DATABASE=endurain

# For MariaDB, use:
# DB_TYPE=mariadb
# DB_HOST=localhost
# DB_PORT=3306

# Security Keys
SECRET_KEY=generate_with_openssl_rand_hex_32
FERNET_KEY=generate_with_fernet_keygen
ALGORITHM=HS256

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Reverse Geo Provider
REVERSE_GEO_PROVIDER=nominatim
NOMINATIM_API_HOST=nominatim.openstreetmap.org
NOMINATIM_API_USE_HTTPS=true
REVERSE_GEO_RATE_LIMIT=1

# Jaeger Tracing (Optional)
JAEGER_ENABLED=false

# SMTP Configuration (Optional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
```

Generate the required secrets:

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate FERNET_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy these generated values and paste them into your `.env` file.

### 7. Run Database Migrations

Initialize the database schema:

```bash
cd /opt/endurain/backend
poetry run alembic upgrade head
```

### 8. Setup Frontend

Exit the endurain user (or open a new terminal) and build the frontend:

```bash
cd /opt/endurain/frontend/app
npm install
npm run build
```

The built files will be in `/opt/endurain/frontend/app/dist`.

### 9. Create Systemd Service

Exit the endurain user and create a systemd service file:

```bash
sudo nano /etc/systemd/system/endurain.service
```

Add the following content:

```ini
[Unit]
Description=Endurain Backend Service
After=network.target postgresql.service
# Or use mariadb.service if using MariaDB
# After=network.target mariadb.service

[Service]
Type=simple
User=endurain
Group=endurain
WorkingDirectory=/opt/endurain/backend
Environment="PATH=/opt/endurain/.local/bin:/usr/bin"
ExecStart=/home/endurain/.local/bin/poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable endurain
sudo systemctl start endurain
```

Check the service status:

```bash
sudo systemctl status endurain
```

### 10. Setup Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt install -y nginx
```

Create an Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/endurain
```

Add the following content:

```nginx
server {
    listen 80;
    server_name endurain.yourdomain.com;

    # Frontend
    location / {
        root /opt/endurain/frontend/app/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 100M;
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/endurain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 11. Setup SSL with Let's Encrypt (Recommended)

Install Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

Obtain and install SSL certificate:

```bash
sudo certbot --nginx -d endurain.yourdomain.com
```

Follow the prompts. Certbot will automatically configure Nginx for HTTPS.

### 12. Alternative: Using Caddy as Reverse Proxy

If you prefer Caddy over Nginx:

```bash
sudo apt install -y caddy
```

Create a Caddyfile:

```bash
sudo nano /etc/caddy/Caddyfile
```

Add the following content:

```
endurain.yourdomain.com {
    # Backend API
    handle /api/* {
        reverse_proxy localhost:8000
    }

    # WebSocket
    handle /ws/* {
        reverse_proxy localhost:8000
    }

    # Frontend
    handle {
        root * /opt/endurain/frontend/app/dist
        try_files {path} /index.html
        file_server
    }
}
```

Restart Caddy:

```bash
sudo systemctl restart caddy
```

Caddy will automatically obtain and renew SSL certificates.

## Default Credentials

After installation, access your Endurain instance at your configured domain:

- **Username:** admin
- **Password:** admin

**Important:** Change the default password immediately after first login!

## Updating Endurain

To update your bare metal installation:

```bash
# Stop the service
sudo systemctl stop endurain

# Switch to endurain user
sudo su - endurain
cd /opt/endurain

# Pull latest changes
git pull

# Update backend dependencies
cd /opt/endurain/backend
poetry install --no-root

# Run migrations
poetry run alembic upgrade head

# Exit endurain user
exit

# Rebuild frontend
cd /opt/endurain/frontend/app
npm install
npm run build

# Start the service
sudo systemctl start endurain
```

## Troubleshooting

### Check Backend Logs

```bash
sudo journalctl -u endurain -f
```

### Check Nginx Logs

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Database Connection Issues

Verify database credentials in `/opt/endurain/backend/.env` and ensure the database service is running:

```bash
# For PostgreSQL
sudo systemctl status postgresql

# For MariaDB
sudo systemctl status mariadb
```

### Permission Issues

Ensure proper ownership of application files:

```bash
sudo chown -R endurain:endurain /opt/endurain
```

### Frontend Not Loading

Verify the frontend was built successfully and files exist:

```bash
ls -la /opt/endurain/frontend/app/dist
```

## Performance Optimization

### Use a Production WSGI Server

For better performance, consider using Gunicorn with Uvicorn workers:

```bash
cd /opt/endurain/backend
poetry add gunicorn
```

Update the systemd service ExecStart line:

```ini
ExecStart=/home/endurain/.local/bin/poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Database Connection Pooling

Endurain uses SQLAlchemy which includes connection pooling by default. For high-traffic instances, you may need to adjust pool settings in the application configuration.

### Enable Compression

Add this to your Nginx configuration inside the `server` block:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

## Security Considerations

1. **Firewall:** Use UFW or iptables to restrict access to only necessary ports
2. **Regular Updates:** Keep your system and dependencies updated
3. **Database Security:** Use strong passwords and restrict database access to localhost
4. **File Permissions:** Ensure application files are not world-readable
5. **HTTPS Only:** Always use HTTPS in production
6. **Backups:** Regularly backup your database and activity files

## Backup and Restore

### Backup

```bash
# Database backup (PostgreSQL)
sudo -u postgres pg_dump endurain > endurain_backup_$(date +%Y%m%d).sql

# Database backup (MariaDB)
sudo mysqldump -u endurain -p endurain > endurain_backup_$(date +%Y%m%d).sql

# Activity files backup
sudo tar -czf endurain_files_$(date +%Y%m%d).tar.gz /opt/endurain/backend/app/data
```

### Restore

```bash
# Database restore (PostgreSQL)
sudo -u postgres psql endurain < endurain_backup_20241004.sql

# Database restore (MariaDB)
sudo mysql -u endurain -p endurain < endurain_backup_20241004.sql

# Activity files restore
sudo tar -xzf endurain_files_20241004.tar.gz -C /
sudo chown -R endurain:endurain /opt/endurain/backend/app/data
```

## Additional Notes

* This guide assumes a single-server setup. For production deployments with high traffic, consider a distributed setup with separate database and application servers.
* Monitor your application logs regularly for any issues.
* Consider setting up monitoring tools like Prometheus and Grafana for better observability.
* If using Jaeger for tracing, you'll need to install and configure it separately.

For more information, refer to the [Advanced Configuration Guide](advanced-started.md).
