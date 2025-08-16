#!/bin/bash

# SocFinder Server Monitoring Script

echo "🖥️  SocFinder Server Monitor"
echo "=================================="
echo ""

# System Info
echo "📋 SYSTEM INFO"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime -p)"
echo "Date: $(date)"
echo ""

# CPU Info
echo "💻 CPU INFO"
echo "CPU Model: $(cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | xargs)"
echo "CPU Cores: $(nproc)"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

# Memory Usage
echo "🧠 MEMORY USAGE"
free -h
echo ""
echo "Memory Usage:"
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
USED_MEM=$(free -m | awk 'NR==2{printf "%.0f", $3}')
FREE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $4}')
AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
MEM_PERCENT=$(awk "BEGIN {printf \"%.1f\", ($USED_MEM/$TOTAL_MEM)*100}")

echo "  Total: ${TOTAL_MEM}MB"
echo "  Used: ${USED_MEM}MB (${MEM_PERCENT}%)"
echo "  Free: ${FREE_MEM}MB"
echo "  Available: ${AVAILABLE_MEM}MB"

if [ "$AVAILABLE_MEM" -lt 200 ]; then
    echo "  ⚠️  WARNING: Low memory!"
elif [ "$AVAILABLE_MEM" -lt 100 ]; then
    echo "  🚨 CRITICAL: Very low memory!"
fi
echo ""

# Disk Usage
echo "💾 DISK USAGE"
df -h
echo ""

# Check if disk usage is high
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  WARNING: Disk usage is ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -gt 90 ]; then
    echo "🚨 CRITICAL: Disk usage is ${DISK_USAGE}%"
fi
echo ""

# Top processes by memory
echo "🔝 TOP PROCESSES BY MEMORY"
ps aux --sort=-%mem | head -6 | awk '{printf "%-10s %-6s %-6s %-20s\n", $1, $3"%", $4"%", $11}'
echo ""

# Top processes by CPU
echo "🔥 TOP PROCESSES BY CPU"
ps aux --sort=-%cpu | head -6 | awk '{printf "%-10s %-6s %-6s %-20s\n", $1, $3"%", $4"%", $11}'
echo ""

# Docker containers status
echo "🐳 DOCKER CONTAINERS"
if command -v docker &> /dev/null; then
    if docker ps -q > /dev/null 2>&1; then
        echo "Running containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        
        # Docker resource usage
        echo "📊 DOCKER RESOURCE USAGE"
        timeout 5 docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
        echo ""
        
        # Docker disk usage
        echo "💿 DOCKER DISK USAGE"
        docker system df
        echo ""
    else
        echo "Docker is not running or no containers found"
        echo ""
    fi
else
    echo "Docker is not installed"
    echo ""
fi

# SocFinder specific checks
echo "🎯 SOCFINDER STATUS"
if [ -f "docker-compose.yml" ] || [ -f "docker-compose.prod.yml" ] || [ -f "docker-compose.minimal.yml" ]; then
    # Check which compose file exists
    COMPOSE_FILE=""
    if [ -f "docker-compose.minimal.yml" ]; then
        COMPOSE_FILE="docker-compose.minimal.yml"
        echo "Configuration: MINIMAL (1GB RAM optimized)"
    elif [ -f "docker-compose.prod.yml" ]; then
        COMPOSE_FILE="docker-compose.prod.yml"
        echo "Configuration: PRODUCTION"
    elif [ -f "docker-compose.yml" ]; then
        COMPOSE_FILE="docker-compose.yml"
        echo "Configuration: DEVELOPMENT"
    fi
    
    if [ ! -z "$COMPOSE_FILE" ]; then
        echo "Services status:"
        docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null || echo "SocFinder is not running"
        
        # Check if services are accessible
        echo ""
        echo "Service health checks:"
        
        # Backend health
        if curl -f http://localhost/health > /dev/null 2>&1; then
            echo "  ✅ Backend: Healthy"
        elif curl -f http://localhost:8001/health > /dev/null 2>&1; then
            echo "  ✅ Backend: Healthy (port 8001)"
        else
            echo "  ❌ Backend: Not responding"
        fi
        
        # Frontend check
        if curl -f http://localhost > /dev/null 2>&1; then
            echo "  ✅ Frontend: Accessible"
        elif curl -f http://localhost:3000 > /dev/null 2>&1; then
            echo "  ✅ Frontend: Accessible (port 3000)"
        else
            echo "  ❌ Frontend: Not accessible"
        fi
        
        # Database check
        if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U socfinder > /dev/null 2>&1; then
            echo "  ✅ Database: Ready"
        else
            echo "  ❌ Database: Not ready"
        fi
    fi
else
    echo "SocFinder not found in current directory"
fi
echo ""

# Network connections
echo "🌐 NETWORK CONNECTIONS"
echo "Listening ports:"
ss -tlnp | grep -E ":(80|443|3000|5432|8000|8001)" | awk '{print $1, $4}' || netstat -tlnp | grep -E ":(80|443|3000|5432|8000|8001)" | awk '{print $1, $4}'
echo ""

# System load recommendation
echo "💡 RECOMMENDATIONS"
if [ "$AVAILABLE_MEM" -lt 100 ]; then
    echo "  🚨 Consider restarting services or adding more RAM"
fi

if [ "$DISK_USAGE" -gt 85 ]; then
    echo "  🧹 Clean up disk space: docker system prune -f"
fi

LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | xargs)
LOAD_COMPARE=$(awk "BEGIN {print ($LOAD_AVG > $(nproc))}")
if [ "$LOAD_COMPARE" -eq 1 ]; then
    echo "  ⚡ High CPU load - consider optimizing or upgrading"
fi

echo ""
echo "🔄 To run this monitor continuously: watch -n 30 ./monitor.sh"
echo "📊 For real-time stats: htop or docker stats"
