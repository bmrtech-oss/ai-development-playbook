# Troubleshooting Guide

**Last Updated:** 2026-04-18

A collection of common issues and quick fixes. If your issue isn't here, add it.

---

## Setup & Environment

### Issue: `tree-sitter` build fails with "Command 'gcc' not found"

**Symptom:** Installing dependencies fails during `npm install` or `poetry install`.

**Fix (Linux/WSL):**
```bash
apt-get update && apt-get install -y build-essential python3-dev
npm install  # Retry
```

**Fix (macOS):**
```bash
xcode-select --install  # Install Xcode command line tools
npm install  # Retry
```

**Fix (Windows/WSL2):**
```bash
wsl --install
# In WSL terminal:
apt-get update && apt-get install -y build-essential python3-dev
```

---

### Issue: Docker port 5432 already in use

**Symptom:** `docker-compose up` fails: "Port 5432 is already allocated"

**Fix:**
```bash
# Check what's using the port
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows

# Option 1: Kill the process
kill -9 <PID>

# Option 2: Use a different port in docker-compose.yml
# Change:   5432:5432
# To:       5433:5432
```

---

### Issue: `.env` file not loaded

**Symptom:** API calls fail with "Missing API key" even though `.env` has a value.

**Fix:**
```bash
# Verify .env exists and is readable
ls -la .env

# Check environment is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('MY_KEY'))"

# Or check that your app calls load_dotenv():
# In backend/main.py:
from dotenv import load_dotenv
load_dotenv()  # Must be called before importing config
```

---

## Backend (Python)

### Issue: Poetry lock conflicts

**Symptom:** `poetry install` hangs or reports "Failed to find a version that satisfies all constraints"

**Fix:**
```bash
# Update the lock file
poetry lock --no-update

# Or clear cache and retry
rm poetry.lock
poetry install --no-cache
```

---

### Issue: Pytest fixture not found

**Symptom:** `fixture 'db' not found` error.

**Fix:**
```bash
# Ensure conftest.py is in the correct directory
# Structure should be:
# tests/
#   conftest.py  # Contains @pytest.fixture
#   test_*.py

# If still failing, check that conftest.py imports are correct
python -m pytest tests/ -v  # Run with module path
```

---

### Issue: Mypy errors: "Partial [function]" or "Argument missing for [parameter]"

**Symptom:** Type checking fails despite code running fine.

**Fix (Option 1):** Add type ignore comment
```python
result = foo(bar)  # type: ignore[arg-type]
```

**Fix (Option 2):** Add type annotations
```python
from typing import Optional

def foo(bar: Optional[str] = None) -> str:
    return bar or "default"
```

---

### Issue: SLM model weights fail to load

**Symptom:** `RuntimeError: CUDA out of memory` or "Model not found"

**Fix (out of memory):**
```bash
# Check GPU memory
nvidia-smi

# Option 1: Use a smaller model
# In config:
MODEL_NAME = "distilbert-base-uncased"  # Smaller than BERT-large

# Option 2: Use CPU (slow but works)
device = "cpu"  # Instead of "cuda"
```

**Fix (model not found):**
```bash
# Verify path exists
ls -la gs://models-prod/slm-code-v2.3.0/

# Or download manually
gsutil cp gs://models-prod/slm-code-v2.3.0/weights.bin ./models/
```

---

## Frontend (TypeScript / VS Code Extension)

### Issue: Extension doesn't activate or fails silently

**Symptom:** Pressing Ctrl+Shift+P shows no commands from the extension.

**Fix:**
```bash
# Check that the extension is installed
code --list-extensions | grep your-extension

# If missing, build and install locally
npm run build
npm run compile  # For TypeScript

# In VS Code: Debug -> Start Debugging
# Opens "Extension Development Host" with full logs
```

---

### Issue: Webview not rendering or showing blank

**Symptom:** Extension webview shows empty white screen.

**Fix:**
```typescript
// In extension.ts, ensure webview is properly initialized
const panel = vscode.window.createWebviewPanel(
  'myExtension',
  'My Panel',
  vscode.ViewColumn.One,
  { enableScripts: true }  // Critical!
);

panel.webview.html = getWebviewContent();  // Or use this instead
```

---

### Issue: React component not re-rendering on state change

**Symptom:** State updates but UI doesn't reflect changes.

**Fix (with Zustand):**
```typescript
// Ensure you're using the hook correctly
const { count, increment } = useStore();

// If not working, check that store is exported correctly
export const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
```

---

### Issue: Electron app won't start: "Module not found"

**Symptom:** `Could not find the main process module at /path/to/main.js`

**Fix:**
```bash
# Build TypeScript first
npm run build

# Check that main.js exists in dist/
ls -la dist/main.js

# Or configure main entry point in package.json
{
  "main": "dist/main.js"  # Not "src/main.ts"
}
```

---

### Issue: IPC (Electron Main ↔ Renderer) message not received

**Symptom:** `ipcRenderer.send('msg')` doesn't trigger `ipcMain.on('msg')`

**Fix:**
```typescript
// In preload script (if using preload), expose ipcRenderer
const { ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('ipc', {
  send: (channel, data) => ipcRenderer.send(channel, data),
  on: (channel, func) => ipcRenderer.on(channel, (event, data) => func(data)),
});

// In renderer (React component)
window.ipc.send('my-message', { data: 'hello' });
```

---

## Infrastructure & Deployment

### Issue: Kubectl `Pending` pod (won't start)

**Symptom:** `kubectl get pods` shows `Pending` status for minutes.

**Fix:**
```bash
# Check events for the pod
kubectl describe pod <pod-name> -n default

# Common issues:
# 1. No available nodes: Scale up cluster
# 2. Insufficient resources: Check node capacity
#    kubectl top nodes
# 3. PVC not found: Create PersistentVolumeClaim first

# Debug node
kubectl debug node/<node-name> -it --image=ubuntu
```

---

### Issue: OpenTofu `state lock` - resource already locked

**Symptom:** `Error: Error acquiring the state lock`

**Fix:**
```bash
# Check lock file (if using local state)
ls -la terraform/.terraform.tfstate.lock.hcl

# Remove lock (dangerous! only if you're sure no other apply is running)
rm terraform/.terraform.tfstate.lock.hcl

# Or force unlock (for GCS backend)
terraform force-unlock <LOCK-ID>

# Better: Wait for the other apply to finish
# Or use: terraform refresh (read-only operation)
```

---

### Issue: CI/CD pipeline fails randomly (flaky test)

**Symptom:** Same test passes locally, fails in CI.

**Fix:**
1. **Check timing:** Add `sleep` or increase timeouts
   ```yaml
   script:
     - timeout 30 pytest tests/test_slow.py
   ```

2. **Check randomness:** Disable test shuffling or use fixed seed
   ```bash
   pytest --tb=short -p no:randomly  # Disable pytest-randomly
   ```

3. **Check environment:** CI environment may be different
   ```bash
   # Reproduce CI environment locally
   docker run --rm -v $PWD:/work python:3.11 /bin/bash
   ```

4. **Increase retries:**
   ```yaml
   retry: 2  # Retry failed jobs
   ```

---

### Issue: GitLab runner not picking up jobs

**Symptom:** Jobs sit in queue forever or run on wrong runner.

**Fix:**
```bash
# Check runner status
gitlab-runner status

# Restart runner
gitlab-runner stop && gitlab-runner start

# Verify runner is registered and online
gitlab-runner verify --delete

# Check job tags match runner tags (in .gitlab-ci.yml):
tags:
  - docker  # Runner must have this tag
```

---

## Database & Vector Search

### Issue: PostgreSQL connection refused

**Symptom:** `psycopg2.OperationalError: could not connect to server`

**Fix:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Or check native install
pg_isready -h localhost -p 5432

# If not running, start it
docker-compose up -d db  # Or: brew services start postgresql
```

---

### Issue: pgvector extension not loaded

**Symptom:** `operator does not exist: vector <-> vector`

**Fix:**
```sql
-- In PostgreSQL, create extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

### Issue: Vector search slow or times out

**Symptom:** `SELECT * FROM embeddings ORDER BY embedding <-> query_vector LIMIT 10` takes > 5s.

**Fix:**
```sql
-- Check index exists
SELECT * FROM pg_indexes WHERE tablename='embeddings';

-- If missing, create index (takes time for large tables)
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Or adjust IVF parameters for speed vs. accuracy
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);
```

---

## AI/ML Issues

### Issue: Prompt engineering: Model gives generic responses

**Symptom:** LLM output is vague or unrelated to the prompt.

**Fix:**
- Add examples (few-shot prompting)
- Be specific: "Generate a Python function..." not "Write code"
- Include constraints: "Max 10 lines"
- Use system prompt: `"You are a Python expert"`

### Issue: Token usage is unexpectedly high

**Symptom:** API costs spike; token count was not budgeted.

**Fix:**
- Check prompt length: `len(prompt.split())`
- Cache prompts: Use Redis for frequently asked questions
- Use cheaper model: Switch from GPT-4 to GPT-3.5-turbo
- Trim responses: Set `max_tokens` parameter

---

## General Debugging Tips

### Enable verbose logging

```bash
# Python
export DEBUG=true
python -m app.main

# Node.js
DEBUG=* npm start

# GitLab CI
# Add to .gitlab-ci.yml:
  variables:
    CI_DEBUG_TRACE: "true"  # Shows all commands (caution: may expose secrets)
```

### Use debuggers

```bash
# Python
python -m pdb app/main.py  # Breakpoint debugger
# Or: import pdb; pdb.set_trace()

# Node.js
node --inspect app.js
# Then open chrome://inspect

# VS Code
# Add .vscode/launch.json for debugging
```

---

## Getting Help

1. **Search this guide** (Ctrl+F / Cmd+F)
2. **Check logs:** `kubectl logs`, `docker logs`, app logs
3. **Ask in Slack:** `#engineering` channel
4. **Open an issue:** Include error message, steps to reproduce, environment
5. **Update this guide:** If you solve something new, add it here

---

## Common Error Messages & Meanings

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| `ModuleNotFoundError: No module named 'X'` | Dependency not installed | `pip install X` or `npm install X` |
| `EADDRINUSE: address already in use :::3000` | Port already taken | Change port or kill process using it |
| `TypeError: Cannot read property 'X' of undefined` | Null/undefined reference | Check initialization order |
| `ConnectionRefusedError: Connection refused` | Service not running | Start service (DB, API, etc.) |
| `SyntaxError: invalid syntax` | Python code error | Check line number and indentation |
| `Timeout waiting for element` | Playwright test too fast | Increase `timeout: 10000` |
