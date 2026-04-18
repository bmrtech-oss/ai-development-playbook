# Local Environment Setup

## Prerequisites
- **OS:** macOS or Linux (WSL2 supported).
- **Python:** 3.11+ (Managed via `pyenv` or `asdf`).
- **Node.js:** 18+ (Managed via `nvm` or `fnm`).
- **Docker:** Required for running local databases (PostgreSQL/pgvector).

## Step 1: Clone and Bootstrap
```bash
git clone https://github.com/bmrtech-oss/ai-development-playbook.git
cd ai-development-playbook
make setup
```

## Step 2: Backend Setup
We use `poetry` for dependency management.
```bash
cd backend
poetry install
poetry shell
```
Create a `.env` file:
```bash
cp .env.example .env
# Add your GCP credentials and LLM API keys
```

## Step 3: Database
Spin up the development stack:
```bash
docker-compose up -d
# This starts PostgreSQL with pgvector and a local RDF store
```
Run migrations:
```bash
alembic upgrade head
```

## Step 4: VS Code Extension Setup
```bash
cd extension
npm install
# Press F5 in VS Code to launch the Extension Development Host
```

## Step 5: Verification
Run the "Inner Loop" health check:
```bash
make test-smoke
```
This verifies that:
1. The backend can connect to Postgres.
2. The `tree-sitter` parser is working for Python/TS.
3. The local SLM (if enabled) can load its weights.

## Common Issues
- **`tree-sitter` build fails:** Ensure you have `build-essential` or Xcode command line tools installed.
- **Docker connection refused:** Check if Docker Desktop is running and the ports (5432) aren't occupied.

For more troubleshooting, see [Troubleshooting Guide](troubleshooting.md).
