#!/bin/bash
# ══════════════════════════════════════════════════════════
# Warm Hook Hugs — Production Deploy Script
# ══════════════════════════════════════════════════════════
# Server: 104.248.171.137 (DigitalOcean)
# Domain: otaskflow.com
# ══════════════════════════════════════════════════════════
# Run on the VPS:
#   chmod +x deploy.sh && sudo ./deploy.sh
# ══════════════════════════════════════════════════════════

set -euo pipefail

DOMAIN="otaskflow.com"
APP_DIR="/opt/warmhookhugs"

echo "═══════════════════════════════════════════════════"
echo "  Warm Hook Hugs — Production Deployment"
echo "  Domain: $DOMAIN"
echo "═══════════════════════════════════════════════════"

# ── 1. Update system packages ──
echo ""
echo "[1/9] Updating system packages..."
apt-get update -y && apt-get upgrade -y

# ── 2. Install Docker ──
echo ""
echo "[2/9] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "  ✓ Docker installed."
else
    echo "  ✓ Docker already installed."
fi

# ── 3. Install Docker Compose (v2 plugin) ──
echo ""
echo "[3/9] Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    apt-get install -y docker-compose-plugin
    echo "  ✓ Docker Compose installed."
else
    echo "  ✓ Docker Compose already installed."
fi

# ── 4. Install Git ──
echo ""
echo "[4/9] Installing Git..."
if ! command -v git &> /dev/null; then
    apt-get install -y git
fi
echo "  ✓ Git ready."

# ── 5. Clone or update repository ──
echo ""
echo "[5/9] Setting up application..."
if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR"
    git pull origin master
    echo "  ✓ Repository updated."
else
    git clone https://github.com/AshfaqueMarfani/warmhookhugs.git "$APP_DIR"
    cd "$APP_DIR"
    echo "  ✓ Repository cloned."
fi

# ── 6. Setup firewall ──
echo ""
echo "[6/9] Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow OpenSSH
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    echo "  ✓ Firewall configured (SSH, HTTP, HTTPS)."
fi

# ── 7. Build and start containers ──
echo ""
echo "[7/9] Building and starting containers..."
cd "$APP_DIR"
docker compose up -d --build

# Wait for DB to be healthy
echo "  Waiting for database..."
sleep 15

# ── 8. Run Django setup ──
echo ""
echo "[8/9] Running Django setup..."
docker compose exec -T web python manage.py migrate --noinput
docker compose exec -T web python manage.py collectstatic --noinput

# Seed data
echo "  Seeding data..."
docker compose exec -T web python seed_data.py
docker compose exec -T web python seed_extra.py

# Create superuser non-interactively
echo "  Creating admin user..."
docker compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@otaskflow.com', 'admin123')
    print('  ✓ Superuser created (admin/admin123)')
else:
    print('  ✓ Superuser already exists.')
"

# ── 9. SSL Certificate ──
echo ""
echo "[9/9] Obtaining SSL certificate..."

# First, test that HTTP is working
echo "  Testing HTTP access..."
sleep 5

# Get SSL certificate from Let's Encrypt
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@otaskflow.com \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    && SSL_OK=true || SSL_OK=false

if [ "$SSL_OK" = true ]; then
    echo "  ✓ SSL certificate obtained!"
    # Swap to SSL nginx config
    cp "$APP_DIR/nginx/ssl.conf" "$APP_DIR/nginx/default.conf"
    docker compose restart nginx
    echo "  ✓ HTTPS enabled!"
else
    echo "  ⚠ SSL failed (DNS may not be pointing here yet)."
    echo "    Run manually later:"
    echo "    docker compose run --rm certbot certonly --webroot -w /var/www/certbot --email admin@otaskflow.com --agree-tos --no-eff-email -d $DOMAIN -d www.$DOMAIN"
    echo "    cp nginx/ssl.conf nginx/default.conf && docker compose restart nginx"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ Deployment Complete!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  HTTP:  http://$DOMAIN"
echo "  HTTPS: https://$DOMAIN (if SSL succeeded)"
echo "  IP:    http://104.248.171.137"
echo "  Admin: http://$DOMAIN/admin/ (admin / admin123)"
echo ""
echo "  ⚠ CHANGE THE ADMIN PASSWORD IMMEDIATELY!"
echo ""
echo "  Useful commands:"
echo "    docker compose logs -f          # View logs"
echo "    docker compose exec web bash    # Shell into Django"
echo "    docker compose restart          # Restart all services"
echo ""
