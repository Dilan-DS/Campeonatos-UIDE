#!/bin/bash
set -euo pipefail
exec > >(tee /var/log/user-data.log) 2>&1

APP_DIR=/opt/campeonatos-uide
PROJECT_DIR="$APP_DIR/CampeonatosUIDE"
COMPOSE_VERSION=v2.32.4

# --- Sistema base ---------------------------------------------------------
dnf update -y
dnf install -y docker git nginx certbot python3-certbot-nginx

# Docker Compose v2: en Amazon Linux 2023 el paquete "docker" NO trae el
# plugin "compose", asi que "docker compose ..." falla. Se instala a mano.
mkdir -p /usr/libexec/docker/cli-plugins
curl -fsSL "https://github.com/docker/compose/releases/download/$${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
  -o /usr/libexec/docker/cli-plugins/docker-compose
chmod +x /usr/libexec/docker/cli-plugins/docker-compose

systemctl enable --now docker nginx
usermod -aG docker ec2-user

# --- Swap ---------------------------------------------------------------
# Un t3.micro tiene 1 GB de RAM. El build de la imagen (pandas, pillow,
# reportlab) y MySQL juntos se quedan sin memoria sin algo de swap.
if [ ! -f /swapfile ]; then
  dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# --- Codigo -----------------------------------------------------------
mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone '${repository_url}' "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only
fi
cd "$PROJECT_DIR"
mkdir -p media staticfiles

# --- Variables de entorno -------------------------------------------------
# Se genera una sola vez. Los secretos (SECRET_KEY, contrasenas MySQL) se
# crean aqui con openssl: nunca pasan por Terraform, ni por el state, ni por
# los argumentos de user-data.
if [ ! -f .env ]; then
  DB_PASS=$(openssl rand -hex 24)
  DB_ROOT_PASS=$(openssl rand -hex 24)
  cat > .env <<EOF
SECRET_KEY=$(openssl rand -base64 48)
DEBUG=False
ALLOWED_HOSTS=${domain_name},www.${domain_name}
CSRF_TRUSTED_ORIGINS=https://${domain_name},https://www.${domain_name}
DATABASE_URL=mysql://${db_user}:$${DB_PASS}@db:3306/${db_name}
MYSQL_DATABASE=${db_name}
MYSQL_USER=${db_user}
MYSQL_PASSWORD=$${DB_PASS}
MYSQL_ROOT_PASSWORD=$${DB_ROOT_PASS}
SECURE_SSL_REDIRECT=False
EOF
  chmod 600 .env
fi

# --- Contenedores -------------------------------------------------------
docker compose up -d --build
# migrate va en el CMD del contenedor web, que espera a que "db" este sano.

# --- Nginx (reverse proxy) --------------------------------------------
cat > /etc/nginx/conf.d/campeonatos-uide.conf <<EOF
server {
    listen 80;
    server_name ${domain_name} www.${domain_name};
    client_max_body_size 5m;

    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header Referrer-Policy same-origin always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    location /media/ {
        alias $PROJECT_DIR/media/;
        access_log off;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
nginx -t && systemctl reload nginx
