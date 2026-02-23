#!/bin/bash
# =============================================================================
# Wateen Project - Production Deployment Script
# =============================================================================
# Usage: ./deploy.sh [command]
# Commands:
#   start     - Build and start all services
#   stop      - Stop all services
#   restart   - Restart all services
#   logs      - Show logs from all services
#   status    - Show status of all services
#   backup    - Create database backup
#   ssl       - Setup SSL certificates
#   migrate   - Run database migrations
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker/docker-compose.yml"
ENV_FILE=".env.production"
PROJECT_NAME="wateen"

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  Wateen Production Deployment"
    echo "=============================================="
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}[CHECK] Verifying prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[ERROR] Docker is not installed${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}[ERROR] Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Check .env.production exists
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}[ERROR] $ENV_FILE not found${NC}"
        echo -e "${YELLOW}[HINT] Copy .env.example to .env.production and configure it${NC}"
        exit 1
    fi
    
    # Check SSL certificates
    if [ ! -f "docker/ssl/fullchain.pem" ] || [ ! -f "docker/ssl/privkey.pem" ]; then
        echo -e "${YELLOW}[WARN] SSL certificates not found in docker/ssl/${NC}"
        echo -e "${YELLOW}[HINT] Run ./deploy.sh ssl to set up certificates${NC}"
    fi
    
    echo -e "${GREEN}[OK] All prerequisites met${NC}"
}

# Start services
start_services() {
    print_banner
    check_prerequisites
    
    echo -e "${YELLOW}[START] Building and starting services...${NC}"
    
    # Pull latest images
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE pull --ignore-pull-failures
    
    # Build images
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE build
    
    # Start services
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
    
    echo -e "${GREEN}[OK] Services started${NC}"
    echo ""
    show_status
}

# Stop services
stop_services() {
    echo -e "${YELLOW}[STOP] Stopping services...${NC}"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
    echo -e "${GREEN}[OK] Services stopped${NC}"
}

# Restart services
restart_services() {
    stop_services
    start_services
}

# Show logs
show_logs() {
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f --tail=100
}

# Show status
show_status() {
    echo -e "${BLUE}[STATUS] Service status:${NC}"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps
    echo ""
    
    # Show health status
    echo -e "${BLUE}[HEALTH] Container health:${NC}"
    for container in wateen_nginx wateen_web wateen_frontend wateen_redis wateen_db; do
        status=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "not running")
        case $status in
            healthy)
                echo -e "  $container: ${GREEN}$status${NC}"
                ;;
            unhealthy)
                echo -e "  $container: ${RED}$status${NC}"
                ;;
            *)
                echo -e "  $container: ${YELLOW}$status${NC}"
                ;;
        esac
    done
}

# Run migrations
run_migrations() {
    echo -e "${YELLOW}[MIGRATE] Running database migrations...${NC}"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec web python manage.py migrate --noinput
    echo -e "${GREEN}[OK] Migrations complete${NC}"
    
    echo -e "${YELLOW}[COLLECTSTATIC] Collecting static files...${NC}"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec web python manage.py collectstatic --noinput
    echo -e "${GREEN}[OK] Static files collected${NC}"
}

# Create backup
create_backup() {
    echo -e "${YELLOW}[BACKUP] Creating database backup...${NC}"
    BACKUP_FILE="backups/wateen_$(date +%Y%m%d_%H%M%S).backup"
    mkdir -p backups
    
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec -T db pg_dump \
        -U wateen_admin \
        -d wateen_prod \
        -F c \
        -f /backups/$(basename $BACKUP_FILE)
    
    # Copy from container
    docker cp wateen_db:/backups/$(basename $BACKUP_FILE) $BACKUP_FILE
    
    echo -e "${GREEN}[OK] Backup created: $BACKUP_FILE${NC}"
}

# Setup SSL
setup_ssl() {
    echo -e "${YELLOW}[SSL] Setting up SSL certificates...${NC}"
    
    read -p "Enter your domain name (e.g., wateen.health): " DOMAIN
    
    if [ -z "$DOMAIN" ]; then
        echo -e "${RED}[ERROR] Domain name is required${NC}"
        exit 1
    fi
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        echo -e "${YELLOW}[INSTALL] Installing certbot...${NC}"
        sudo apt-get update
        sudo apt-get install -y certbot
    fi
    
    # Get certificates
    echo -e "${YELLOW}[CERTBOT] Obtaining certificates for $DOMAIN...${NC}"
    sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN
    
    # Copy certificates
    echo -e "${YELLOW}[COPY] Copying certificates...${NC}"
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem docker/ssl/fullchain.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem docker/ssl/privkey.pem
    
    # Set permissions
    sudo chown $USER:$USER docker/ssl/*.pem
    chmod 600 docker/ssl/privkey.pem
    chmod 644 docker/ssl/fullchain.pem
    
    echo -e "${GREEN}[OK] SSL certificates installed${NC}"
    echo -e "${YELLOW}[HINT] Restart nginx: docker restart wateen_nginx${NC}"
}

# Main command router
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    backup)
        create_backup
        ;;
    ssl)
        setup_ssl
        ;;
    migrate)
        run_migrations
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|backup|ssl|migrate}"
        exit 1
        ;;
esac
