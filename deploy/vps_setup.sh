#!/usr/bin/env bash
set -euo pipefail

# Ubuntu VPS setup for this Django app.
# Usage:
#   1. Copy the repo to your VPS
#   2. Edit the variables below
#   3. Run: bash deploy/vps_setup.sh

APP_NAME="coursebot"
APP_USER="www-data"
PROJECT_DIR="/var/www/coursebot"
VENV_DIR="$PROJECT_DIR/.venv"
DOMAIN_OR_IP="your-server-ip-or-domain"
PORT="8000"
DJANGO_SETTINGS_MODULE="health_project.settings"

echo "==> Installing system packages"
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx

echo "==> Preparing virtual environment"
cd "$PROJECT_DIR"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip wheel
"$VENV_DIR/bin/pip" install -r requirements.txt gunicorn

echo "==> Django environment check"
if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo "WARNING: $PROJECT_DIR/.env not found"
  echo "Create it first, for example:"
  echo "  cp .env.example .env"
  echo "Then add your real GEMINI_API_KEY before continuing."
fi

echo "==> Running database migrations"
"$VENV_DIR/bin/python" manage.py migrate

echo "==> Attempting collectstatic"
if "$VENV_DIR/bin/python" manage.py collectstatic --noinput; then
  echo "collectstatic completed"
else
  echo "collectstatic skipped or failed. This project may need STATIC_ROOT configured for production."
fi

echo "==> Creating systemd service"
sudo tee /etc/systemd/system/${APP_NAME}.service > /dev/null <<EOF
[Unit]
Description=${APP_NAME} gunicorn service
After=network.target

[Service]
User=${APP_USER}
Group=www-data
WorkingDirectory=${PROJECT_DIR}
Environment=DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
ExecStart=${VENV_DIR}/bin/gunicorn --workers 3 --bind 127.0.0.1:${PORT} health_project.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "==> Creating nginx site"
sudo tee /etc/nginx/sites-available/${APP_NAME} > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN_OR_IP};

    client_max_body_size 25M;

    location /static/ {
        alias ${PROJECT_DIR}/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "==> Enabling nginx site"
sudo ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/${APP_NAME}
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

echo "==> Enabling and starting service"
sudo systemctl daemon-reload
sudo systemctl enable ${APP_NAME}
sudo systemctl restart ${APP_NAME}

echo
echo "Setup complete."
echo "Useful commands:"
echo "  sudo systemctl status ${APP_NAME}"
echo "  sudo journalctl -u ${APP_NAME} -f"
echo "  sudo systemctl restart nginx"
echo
echo "Important production notes:"
echo "  - Set DEBUG=False in health_project/settings.py"
echo "  - Set ALLOWED_HOSTS to your VPS IP or domain"
echo "  - Add STATIC_ROOT for collectstatic if you want nginx to serve static files cleanly"
