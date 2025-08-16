#!/bin/bash

# SocFinder Production Deployment Script

set -e  # Exit on any error

echo "🚀 Starting SocFinder deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from example..."
    cp env.prod.example .env
    print_warning "Please edit .env file with your production values before continuing."
    echo "Press Enter to continue after editing .env file..."
    read
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p nginx/ssl
mkdir -p data/backups

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Pull latest images
print_status "Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull postgres nginx

# Build application images
print_status "Building application images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
print_status "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check PostgreSQL
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U socfinder > /dev/null 2>&1; then
    print_success "PostgreSQL is healthy"
else
    print_error "PostgreSQL is not responding"
    exit 1
fi

# Check backend
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_error "Backend is not responding"
    exit 1
fi

# Check frontend
if curl -f http://localhost > /dev/null 2>&1; then
    print_success "Frontend is healthy"
else
    print_error "Frontend is not responding"
    exit 1
fi

print_success "🎉 SocFinder deployed successfully!"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://your-server-ip"
echo "   API: http://your-server-ip/api"
echo "   Health: http://your-server-ip/health"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
echo ""
print_warning "Don't forget to:"
echo "   1. Configure SSL certificates for HTTPS"
echo "   2. Set up domain name and DNS"
echo "   3. Configure firewall rules"
echo "   4. Set up monitoring and backups"
