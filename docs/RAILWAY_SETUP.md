# Railway Deployment Setup

This document describes how to configure Railway deployments for the Level8 project.

## Services

The project deploys two services to Railway:

| Service | Root Directory | Start Command |
|---------|----------------|---------------|
| backend | `src/backend` | `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| frontend | `src/frontend` | `npm run preview -- --host 0.0.0.0 --port $PORT` |

## GitHub Secrets

The CI/CD workflows require Railway tokens to be configured as GitHub secrets.

### Required Secrets

| Secret Name | Description | Source |
|-------------|-------------|--------|
| `RAILWAY_TOKEN` | Token for good-first-design-issue project | `.secrets/railway-gfdi` |

### Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add `RAILWAY_TOKEN` with the value from `.secrets/railway-gfdi`

## Environments

| Environment | Trigger | Token Used |
|-------------|---------|------------|
| PR Preview (`pr-{number}`) | PRs from `agent/feature-*` branches | `RAILWAY_TOKEN` |
| Production | Push to main (src/** changes) or manual | `RAILWAY_TOKEN` |

## Health Checks

The backend exposes a `/health` endpoint that Railway uses to verify the service is running:

```
GET /health
Response: {"status": "ok"}
```

## Local Testing

To test Railway deployment locally:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login (uses token from environment or prompts for login)
railway login

# Deploy backend
cd src/backend
railway up --service backend

# Deploy frontend
cd src/frontend
railway up --service frontend
```
