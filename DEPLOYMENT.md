# CINEIQ Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Fill in all API keys:
  - Clerk (Authentication)
  - TMDB (Movie data)
  - Groq (LLM explanations)
- [ ] Set strong database passwords
- [ ] Generate secure `AWS_SECRET_ACCESS_KEY` for MinIO/S3

### 2. Data & Models
```bash
# Download MovieLens dataset
make download-data

# Ingest TMDB movies
make ingest-tmdb

# Train ML models (SVD + NCF)
make train

# Generate vector embeddings
make build-embeddings
```

### 3. Database Migration
```bash
make migrate
```

## Local Development

```bash
# Start all services
make dev

# Or with rebuild
make dev-build
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090

## Production Deployment

### Option 1: Docker Compose (Simple)

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Option 2: AWS ECS/Fargate

1. **Build and push images:**
```bash
# Backend
docker build -t cineiq-backend:latest ./backend
docker tag cineiq-backend:latest YOUR_ECR_REPO/cineiq-backend:latest
docker push YOUR_ECR_REPO/cineiq-backend:latest

# Frontend
docker build -t cineiq-frontend:latest ./frontend
docker tag cineiq-frontend:latest YOUR_ECR_REPO/cineiq-frontend:latest
docker push YOUR_ECR_REPO/cineiq-frontend:latest
```

2. **Create ECS Task Definitions:**
   - Backend: 2 vCPU, 4GB RAM
   - Frontend: 1 vCPU, 2GB RAM

3. **Set up services:**
   - Application Load Balancer
   - Target Groups
   - Auto Scaling (CPU > 70%)

4. **Managed Services:**
   - RDS PostgreSQL 16 (Multi-AZ)
   - ElastiCache Redis 7
   - EC2 for Qdrant (or ECS task)

### Option 3: Vercel + Railway

**Frontend (Vercel):**
```bash
cd frontend
vercel --prod
```

**Backend (Railway):**
- Connect GitHub repo
- Set environment variables
- Deploy from `backend/` directory

## Environment Variables (Production)

### Backend
```env
DATABASE_URL=postgresql+asyncpg://user:pass@rds-endpoint:5432/cineiq
REDIS_URL=redis://elasticache-endpoint:6379/0
QDRANT_HOST=qdrant-ec2-ip
CLERK_SECRET_KEY=sk_live_...
TMDB_API_KEY=...
GROQ_API_KEY=...
DEBUG=false
```

### Frontend
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_API_URL=https://api.cineiq.com
NEXT_PUBLIC_WS_URL=wss://api.cineiq.com
```

## SSL/TLS Setup

### Using Let's Encrypt (Certbot)
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d cineiq.com -d www.cineiq.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Using AWS Certificate Manager
- Request certificate in ACM
- Validate via DNS
- Attach to ALB

## Monitoring Setup

### Grafana Dashboards
1. Access Grafana: http://your-domain:3001
2. Login: admin/admin (change immediately)
3. Add Prometheus data source: http://prometheus:9090
4. Import dashboards from `monitoring/grafana/dashboards/`

### Alerts
Configure alerts for:
- High error rate (> 5%)
- High latency (p99 > 2s)
- Database connection failures
- Redis connection failures
- Low disk space

## Backup Strategy

### Database Backups
```bash
# Automated daily backups
0 2 * * * pg_dump -h localhost -U cineiq cineiq | gzip > /backups/cineiq_$(date +\%Y\%m\%d).sql.gz

# Retention: 30 days
find /backups -name "cineiq_*.sql.gz" -mtime +30 -delete
```

### Model Backups
```bash
# Backup trained models to S3
aws s3 sync backend/app/ml/models/ s3://cineiq-models/$(date +%Y%m%d)/
```

## Scaling Considerations

### Horizontal Scaling
- Backend: Scale to 3-5 instances behind load balancer
- Frontend: Edge deployment via Vercel/Cloudflare
- Database: Read replicas for analytics queries

### Vertical Scaling
- Qdrant: Increase memory for larger vector collections
- PostgreSQL: Increase connection pool size
- Redis: Increase memory for larger cache

## Security Hardening

1. **Network Security:**
   - Use VPC with private subnets
   - Security groups: Allow only necessary ports
   - Enable VPC Flow Logs

2. **Application Security:**
   - Rate limiting (100 req/min per user)
   - Input validation (Pydantic)
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection (React escaping)

3. **Secrets Management:**
   - Use AWS Secrets Manager or HashiCorp Vault
   - Rotate API keys quarterly
   - Never commit secrets to Git

4. **Monitoring:**
   - Enable CloudWatch/Datadog
   - Set up error tracking (Sentry)
   - Log aggregation (Loki/ELK)

## Performance Optimization

### Backend
- Enable Redis caching (6h TTL for TMDB)
- Use connection pooling (SQLAlchemy)
- Async operations (httpx, asyncpg)
- Load ML models at startup (not per-request)

### Frontend
- Enable Next.js ISR (Incremental Static Regeneration)
- Image optimization (next/image)
- Code splitting (dynamic imports)
- CDN for static assets

### Database
- Create indexes on frequently queried columns
- Vacuum and analyze regularly
- Monitor slow queries

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing environment variables
# - Database connection failed
# - ML models not found (run make train)
```

### Frontend build fails
```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### Database migration fails
```bash
# Reset migrations (CAUTION: data loss)
cd backend
alembic downgrade base
alembic upgrade head
```

## Health Checks

### Backend
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "dependencies": {
    "redis": "ok",
    "qdrant": "ok",
    "postgres": "ok"
  }
}
```

### Frontend
```bash
curl http://localhost:3000
```

Should return 200 OK with HTML.

## Rollback Procedure

1. **Identify last working version:**
```bash
git log --oneline
```

2. **Rollback Docker images:**
```bash
docker-compose down
git checkout <commit-hash>
docker-compose up -d
```

3. **Rollback database (if needed):**
```bash
cd backend
alembic downgrade -1
```

## Support & Maintenance

- Monitor error rates daily
- Review logs weekly
- Update dependencies monthly
- Retrain ML models quarterly
- Security patches: Apply immediately

## Cost Estimation (AWS)

**Monthly costs (estimated):**
- ECS Fargate (2 tasks): $50-100
- RDS PostgreSQL (t3.medium): $60
- ElastiCache Redis (cache.t3.micro): $15
- EC2 for Qdrant (t3.medium): $30
- ALB: $20
- Data transfer: $20-50
- **Total: ~$200-300/month**

## Contact

For deployment issues:
- GitHub Issues: [your-repo]/issues
- Email: support@cineiq.com
- Slack: #cineiq-deployment
