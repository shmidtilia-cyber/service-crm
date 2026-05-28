#!/usr/bin/env bash
set -e

APP_DIR=/var/www/service-crm
REPO_URL=https://github.com/shmidtilia-cyber/service-crm.git
DOMAIN=crm-fadeev.ru

apt update
apt install -y python3 python3-venv python3-pip git nginx postgresql postgresql-contrib

mkdir -p /var/www

if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  cd "$APP_DIR"
  git pull
fi

cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Edit $APP_DIR/.env before production start"
fi

python manage.py migrate || true
python manage.py collectstatic --noinput || true

cp deploy/systemd/service-crm.service /etc/systemd/system/service-crm.service
cp deploy/nginx/site.conf /etc/nginx/sites-available/service-crm
ln -sf /etc/nginx/sites-available/service-crm /etc/nginx/sites-enabled/service-crm
rm -f /etc/nginx/sites-enabled/default

systemctl daemon-reload
systemctl enable service-crm
systemctl restart service-crm
nginx -t
systemctl restart nginx

echo "Service CRM deployed on $DOMAIN"
