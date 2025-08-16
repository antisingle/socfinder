#!/bin/bash

# Test production build locally

echo "🧪 Testing production build locally..."

# Create test .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating test .env file..."
    cat > .env << EOF
POSTGRES_PASSWORD=test_password_123
API_URL=http://localhost/api
EOF
fi

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Build and start
echo "Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services
echo "Waiting for services to start..."
sleep 30

# Test services
echo "Testing services..."

# Test backend health
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
    exit 1
fi

# Test frontend
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
    exit 1
fi

# Test API
if curl -f http://localhost/api/v1/stats/overview > /dev/null 2>&1; then
    echo "✅ API is working"
else
    echo "❌ API is not responding"
    exit 1
fi

echo ""
echo "🎉 Production build test successful!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost"
echo "   API: http://localhost/api"
echo "   Health: http://localhost/health"
echo ""
echo "📊 Service status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "To stop: docker-compose -f docker-compose.prod.yml down"
