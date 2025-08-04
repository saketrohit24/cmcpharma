# CMC Regulatory Writer - Docker Deployment Makefile

.PHONY: help dev prod build clean logs stop restart status health

# Default target
help:
	@echo "CMC Regulatory Writer - Docker Deployment Commands"
	@echo "=================================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev         - Start development environment"
	@echo "  make dev-build   - Build and start development environment"
	@echo ""
	@echo "Production:"
	@echo "  make prod        - Start production environment"
	@echo "  make prod-build  - Build and start production environment"
	@echo ""
	@echo "Management:"
	@echo "  make build       - Build all containers"
	@echo "  make stop        - Stop all containers"
	@echo "  make restart     - Restart all containers"
	@echo "  make clean       - Remove containers and volumes"
	@echo "  make logs        - View logs"
	@echo "  make status      - Show container status"
	@echo "  make health      - Check service health"
	@echo ""
	@echo "Setup:"
	@echo "  make setup       - Initial setup (copy env file)"
	@echo ""

# Development environment
dev:
	@echo "Starting development environment..."
	docker-compose up -d

dev-build:
	@echo "Building and starting development environment..."
	docker-compose up -d --build

# Production environment
prod:
	@echo "Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d

prod-build:
	@echo "Building and starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d --build

# Build containers
build:
	@echo "Building all containers..."
	docker-compose build

# Initial setup
setup:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		echo "Copying .env.docker to .env..."; \
		cp .env.docker .env; \
		echo "Please edit .env file with your actual API keys"; \
	else \
		echo ".env file already exists"; \
	fi

# Management commands
stop:
	@echo "Stopping all containers..."
	docker-compose down
	docker-compose -f docker-compose.prod.yml down

restart:
	@echo "Restarting containers..."
	docker-compose restart
	docker-compose -f docker-compose.prod.yml restart

clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	docker system prune -f

# Monitoring
logs:
	@echo "Showing logs..."
	docker-compose logs -f

logs-backend:
	@echo "Showing backend logs..."
	docker-compose logs -f backend

logs-frontend:
	@echo "Showing frontend logs..."
	docker-compose logs -f frontend

status:
	@echo "Container status:"
	docker-compose ps
	@echo ""
	@echo "Production status:"
	docker-compose -f docker-compose.prod.yml ps

health:
	@echo "Checking service health..."
	@echo "Backend health:"
	@curl -f http://localhost:8001/api/health 2>/dev/null && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"
	@echo "Frontend health:"
	@curl -f http://localhost/ 2>/dev/null && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"

# Quick deployment recipes
quick-dev: setup dev-build
	@echo "Development environment is starting..."
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost:8001"

quick-prod: setup prod-build
	@echo "Production environment is starting..."
	@echo "Application: http://localhost"