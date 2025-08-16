#!/bin/bash

# SocFinder Minimal Deployment Script для серверов с 1GB RAM

set -e  # Exit on any error

echo "🚀 Starting SocFinder MINIMAL deployment for 1GB RAM server..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка ресурсов сервера
print_status "Checking server resources..."
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
CPU_CORES=$(nproc)

echo "💻 Server specs:"
echo "   RAM: ${TOTAL_MEM}MB total, ${AVAILABLE_MEM}MB available"
echo "   CPU: ${CPU_CORES} cores"

if [ "$TOTAL_MEM" -lt 900 ]; then
    print_error "Server has less than 900MB RAM. SocFinder requires at least 1GB."
    exit 1
fi

if [ "$AVAILABLE_MEM" -lt 600 ]; then
    print_warning "Low available memory (${AVAILABLE_MEM}MB). Consider stopping other services."
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Setup environment
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating minimal configuration..."
    cat > .env << EOF
POSTGRES_PASSWORD=socfinder_minimal_$(date +%s)
API_URL=http://$(hostname -I | awk '{print $1}')/api
EOF
    print_success "Created .env file with auto-generated password"
fi

# Enable swap if not exists (важно для 1GB RAM!)
if [ ! -f /swapfile ]; then
    print_status "Creating 1GB swap file for better performance..."
    sudo fallocate -l 1G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    print_success "Swap file created and activated"
fi

# Настройка системы для экономии памяти
print_status "Optimizing system for low memory..."
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.minimal.yml down || true

# Cleanup old images to save space
print_status "Cleaning up old Docker images..."
docker system prune -f

# Build with minimal resources
print_status "Building images with memory limits..."
export DOCKER_BUILDKIT=1
docker-compose -f docker-compose.minimal.yml build

# Start services
print_status "Starting services with resource limits..."
docker-compose -f docker-compose.minimal.yml up -d

# Wait for services
print_status "Waiting for services to start (this may take 2-3 minutes on slow server)..."
sleep 90

# Check health
print_status "Checking service health..."

if docker-compose -f docker-compose.minimal.yml exec -T postgres pg_isready -U socfinder > /dev/null 2>&1; then
    print_success "PostgreSQL is healthy"
else
    print_error "PostgreSQL is not responding"
    docker-compose -f docker-compose.minimal.yml logs postgres
    exit 1
fi

# Check if backend is loading data
print_status "Checking backend status (data loading may take 5-10 minutes)..."
for i in {1..30}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
        break
    else
        if [ $i -eq 30 ]; then
            print_error "Backend is not responding after 5 minutes"
            docker-compose -f docker-compose.minimal.yml logs backend
            exit 1
        fi
        echo -n "."
        sleep 10
    fi
done

print_success "🎉 SocFinder MINIMAL deployed successfully!"
echo ""
print_warning "⚠️  IMPORTANT NOTES FOR 1GB RAM SERVER:"
echo "   • Data loading takes 5-10 minutes on first start"
echo "   • Expect slower performance with multiple users"
echo "   • Monitor memory usage: docker stats"
echo "   • Restart if system becomes unresponsive"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://$(hostname -I | awk '{print $1}')"
echo "   API: http://$(hostname -I | awk '{print $1}')/api"
echo ""
echo "📊 Resource monitoring:"
echo "   docker stats"
echo "   free -h"
echo "   df -h"
echo ""
echo "🔧 Management commands:"
echo "   Status: docker-compose -f docker-compose.minimal.yml ps"
echo "   Logs: docker-compose -f docker-compose.minimal.yml logs -f"
echo "   Stop: docker-compose -f docker-compose.minimal.yml down"
echo "   Restart: docker-compose -f docker-compose.minimal.yml restart"
