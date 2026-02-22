#!/bin/bash
# ══════════════════════════════════════════════════════════
# Warm Hook Hugs — Production Deploy Script
# ══════════════════════════════════════════════════════════
# Run on a fresh Ubuntu server:
#   chmod +x deploy.sh && sudo ./deploy.sh
# ══════════════════════════════════════════════════════════

set -euo pipefail

echo "═══════════════════════════════════════════════════"
echo "  Warm Hook Hugs — Production Deployment"
echo "═══════════════════════════════════════════════════"

# ── 1. Update system packages ──
echo "[1/7] Updating system packages..."
apt-get update -y && apt-get upgrade -y

# ── 2. Install Docker ──
echo "[2/7] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installed successfully."
else
    echo "Docker already installed."
fi

# ── 3. Install Docker Compose (v2 plugin) ──
echo "[3/7] Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    apt-get install -y docker-compose-plugin
    echo "Docker Compose installed successfully."
else
    echo "Docker Compose already installed."
fi

# ── 4. Setup environment file ──
echo "[4/7] Setting up environment file..."
if [ ! -f .env.prod ]; then
    cp .env.example .env.prod
    echo "⚠️  IMPORTANT: Edit .env.prod with your actual secrets before proceeding!"
    echo "    nano .env.prod"
    echo ""
    read -p "Press Enter after editing .env.prod to continue..."
fi

# ── 5. Build and start containers ──
echo "[5/7] Building and starting containers..."
docker compose up -d --build

# Wait for DB to be ready
echo "Waiting for database to be ready..."
sleep 10

# ── 6. Run Django migrations & collect static ──
echo "[6/7] Running migrations and collecting static files..."
docker compose exec web python manage.py migrate --noinput
docker compose exec web python manage.py collectstatic --noinput

# ── 7. Create superuser ──
echo "[7/7] Creating Django superuser..."
echo "Enter superuser credentials:"
docker compose exec -it web python manage.py createsuperuser

echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ Deployment Complete!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "  Your site is running at: http://$(hostname -I | awk '{print $1}')"
echo "  Admin panel: http://$(hostname -I | awk '{print $1}')/admin/"
echo ""
echo "  Next steps:"
echo "  1. Point your domain DNS to this server's IP"
echo "  2. Update nginx/default.conf with your domain"
echo "  3. Run: docker compose exec certbot certbot certonly --webroot -w /var/www/certbot -d yourdomain.com"
echo "  4. Restart nginx: docker compose restart nginx"
echo ""
