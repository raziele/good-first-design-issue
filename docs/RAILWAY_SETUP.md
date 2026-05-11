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
| PR Preview (`pr-{number}`) | PRs from `agent/feature-*` branches **or** manual `workflow_dispatch` | `RAILWAY_TOKEN` |
| Production | Push to main (src/** changes) or manual | `RAILWAY_TOKEN` |

### Preview when the PR was opened by CI (`GITHUB_TOKEN`)

The specs-to-code job opens the agent PR with `GITHUB_TOKEN`. GitHub **does not** run other workflows from that event (no recursive workflow runs), so **Preview Deploy (Railway)** will usually **not** start automatically for those PRs.

After the workflow on **`main`** includes `workflow_dispatch` for preview deploy, run manually:

```bash
gh workflow run preview-deploy.yml \
  -f ref=agent/feature-<RUN_ID> \
  -f pr_number=<PR_NUMBER>
```

Example for PR **20** whose head branch is `agent/feature-25692212336`:

```bash
gh workflow run preview-deploy.yml \
  -f ref=agent/feature-25692212336 \
  -f pr_number=20
```

### Preview from your laptop (no GitHub Actions)

From repo root, with `RAILWAY_TOKEN` set (or after `railway login`):

```bash
export PR=20   # GitHub PR number → Railway env pr-20
(cd src/backend && railway up --service backend --environment "pr-${PR}")
(cd src/frontend && railway up --service frontend --environment "pr-${PR}")
```

Then use the Railway dashboard or `railway status` for that environment to get URLs.

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
