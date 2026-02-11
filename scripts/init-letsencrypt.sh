#!/bin/bash
# Bootstrap script for initial SSL certificate setup with Let's Encrypt.
# Solves the chicken-and-egg problem: nginx needs certs to start,
# certbot needs nginx to validate the domain.
#
# Usage: ./scripts/init-letsencrypt.sh
# Run from the project root directory.

set -euo pipefail

# ---- Configuration (from .env or defaults) ----
if [ -f .env ]; then
    # shellcheck disable=SC1091
    source .env
fi

DOMAIN="${DOMAIN:?Error: DOMAIN is not set. Add it to .env}"
EMAIL="${CERTBOT_EMAIL:?Error: CERTBOT_EMAIL is not set. Add it to .env}"
COMPOSE_FILE="docker-compose.prod.yml"
DATA_PATH="certbot_certs"  # Docker volume name

RSA_KEY_SIZE=4096
STAGING="${STAGING:-0}"  # Set STAGING=1 for testing (avoids rate limits)

# ---- Colors ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ---- Pre-flight checks ----
info "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || error "docker is not installed"
command -v docker compose >/dev/null 2>&1 || error "docker compose is not installed"
[ -f "$COMPOSE_FILE" ] || error "$COMPOSE_FILE not found. Run from project root."

# Check DNS
info "Checking DNS for $DOMAIN..."
RESOLVED_IP=$(dig +short "$DOMAIN" 2>/dev/null | head -1 || true)
if [ -z "$RESOLVED_IP" ]; then
    warn "Could not resolve $DOMAIN via DNS. Make sure A record points to this server."
    warn "Continuing anyway (DNS propagation may still be in progress)..."
else
    info "DNS resolves $DOMAIN -> $RESOLVED_IP"
fi

# ---- Step 1: Download recommended TLS parameters ----
info "Downloading recommended TLS parameters..."

# Create a temporary container to populate the certbot_certs volume
docker compose -f "$COMPOSE_FILE" run --rm --no-deps \
    --entrypoint "sh -c" certbot \
    "mkdir -p /etc/letsencrypt && \
     wget -qO /etc/letsencrypt/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf && \
     wget -qO /etc/letsencrypt/ssl-dhparams.pem https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem && \
     echo 'TLS parameters downloaded successfully'"

# ---- Step 2: Create temporary self-signed certificate ----
info "Creating temporary self-signed certificate for $DOMAIN..."

docker compose -f "$COMPOSE_FILE" run --rm --no-deps \
    --entrypoint "sh -c" certbot \
    "mkdir -p /etc/letsencrypt/live/$DOMAIN && \
     openssl req -x509 -nodes -newkey rsa:$RSA_KEY_SIZE -days 1 \
       -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
       -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
       -subj '/CN=localhost' && \
     echo 'Self-signed certificate created'"

# ---- Step 3: Start nginx with self-signed cert ----
info "Starting nginx with temporary certificate..."
docker compose -f "$COMPOSE_FILE" up -d nginx
info "Waiting for nginx to start..."
sleep 5

# ---- Step 4: Delete self-signed certificate ----
info "Removing temporary self-signed certificate..."
docker compose -f "$COMPOSE_FILE" run --rm --no-deps \
    --entrypoint "sh -c" certbot \
    "rm -rf /etc/letsencrypt/live/$DOMAIN && \
     rm -rf /etc/letsencrypt/archive/$DOMAIN && \
     rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf && \
     echo 'Temporary certificate removed'"

# ---- Step 5: Request real certificate from Let's Encrypt ----
info "Requesting Let's Encrypt certificate for $DOMAIN..."

STAGING_ARG=""
if [ "$STAGING" = "1" ]; then
    STAGING_ARG="--staging"
    warn "Using Let's Encrypt STAGING environment (not production)"
fi

docker compose -f "$COMPOSE_FILE" run --rm --no-deps \
    --entrypoint "certbot certonly --webroot \
        -w /var/www/certbot \
        $STAGING_ARG \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --rsa-key-size $RSA_KEY_SIZE \
        -d $DOMAIN \
        -d www.$DOMAIN \
        --force-renewal" \
    certbot

# ---- Step 6: Reload nginx with real certificate ----
info "Reloading nginx with real certificate..."
docker exec studyhelper-nginx nginx -s reload

# ---- Step 7: Start certbot renewal container ----
info "Starting certbot renewal container..."
docker compose -f "$COMPOSE_FILE" up -d certbot

# ---- Done ----
echo ""
info "SSL setup complete!"
info "  https://$DOMAIN should now be accessible."
info "  Certbot will auto-renew certificates every 12 hours."
echo ""
if [ "$STAGING" = "1" ]; then
    warn "You used STAGING mode. To get a real certificate, run:"
    warn "  STAGING=0 ./scripts/init-letsencrypt.sh"
fi
