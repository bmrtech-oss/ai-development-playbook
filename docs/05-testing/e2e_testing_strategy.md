# End-to-End Testing Strategy

**Last Updated:** 2026-04-18  
**Owner:** QA / DX Team

## Overview

We use **Playwright** for E2E testing of critical user journeys. Tests verify that the full stack (backend + VS Code extension + Electron desktop app) works end-to-end without mocking.

---

## Test Pyramid (AI-Aware)

```
            E2E (Playwright)
              /  VS Code ext
             /   Electron app
            /    User workflows
           /______________________
          /    Integration Tests
         /     API + SLM harness
        /      Mock external APIs
       /_____________________________
      /          Unit Tests
     /           Functions, classes
    /            Fast, no I/O
   /____________________________________
```

**Target split:**
- Unit: 70%
- Integration: 20%
- E2E: 10%

---

## Playwright Setup

### Installation

```bash
npm install -D @playwright/test @playwright/test-gui

# Browsers
npx playwright install chromium firefox webkit
npx playwright install-deps  # System dependencies
```

### Configuration

`playwright.config.ts`:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: process.env.CI ? true : false,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 4,  // Parallel workers
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }],
    process.env.CI ? ['github'] : ['list'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## VS Code Extension E2E Tests

### Test Data Setup

Before running extension tests, seed a test repository:

```bash
# Create a test workspace with known files
mkdir -p /tmp/test-workspace/src
cat > /tmp/test-workspace/src/example.py << 'EOF'
def hello_world():
    return "Hello, World!"
EOF

git init /tmp/test-workspace
git config user.email "test@example.com"
git config user.name "Test User"
git add .
git commit -m "Initial commit"
```

### Example: Test Code Completion in Extension

`tests/e2e/vscode-extension/completion.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test.describe('VS Code Extension - Code Completion', () => {
  let vscodeWindow;

  test.beforeAll(async () => {
    // Launch VS Code with the test workspace
    vscodeWindow = await new Promise((resolve) => {
      const { execSync } = require('child_process');
      execSync('code --new-window /tmp/test-workspace');
      resolve(true);
    });
  });

  test('should show inline completion for Python', async ({ page }) => {
    // Open a Python file
    page.keyboard.press('Control+K');
    page.keyboard.press('Control+O');
    page.keyboard.type('/tmp/test-workspace/src/example.py');
    page.keyboard.press('Enter');

    // Position cursor at end of file
    page.keyboard.press('Control+End');

    // Trigger completion (Cmd+I on Mac, Ctrl+I on Linux/Windows)
    page.keyboard.press('Control+i');

    // Wait for suggestion popup
    const suggestion = page.locator('[role="listbox"]').first();
    await expect(suggestion).toBeVisible({ timeout: 2000 });

    // Check that suggestions are shown
    const items = await page.locator('[role="option"]').count();
    expect(items).toBeGreaterThan(0);
  });

  test('should jump to definition', async ({ page }) => {
    page.keyboard.press('Control+Click');  // On "hello_world"
    
    // Verify we're now at the definition
    const editor = page.locator('[class*="line-content"]').first();
    expect(editor).toContainText('def hello_world');
  });
});
```

---

## Electron Desktop App E2E Tests

### Test: Launch & Search

`tests/e2e/electron/search.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';
import { _electron as electron } from 'playwright';

test.describe('Electron App - Code Search', () => {
  let app;
  let window;

  test.beforeAll(async () => {
    // Launch Electron app
    app = await electron.launch({ args: ['src/index.ts'] });
    window = await app.firstWindow();
  });

  test.afterAll(async () => {
    await app.close();
  });

  test('should search repositories', async () => {
    // Click search input
    const searchInput = window.locator('[placeholder="Search code..."]');
    await searchInput.click();
    await searchInput.type('function');

    // Press Enter
    await window.keyboard.press('Enter');

    // Wait for results
    const results = window.locator('[data-testid="search-result"]');
    await expect(results.first()).toBeVisible({ timeout: 5000 });

    // Verify result count
    const count = await results.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should stream AI-generated explanation', async () => {
    // Navigate to a code snippet
    const codeBlock = window.locator('[class*="code-line"]').first();
    await codeBlock.click();

    // Right-click for context menu
    await codeBlock.click({ button: 'right' });

    // Click "Explain with AI"
    const explainOption = window.locator('text=Explain with AI');
    await explainOption.click();

    // Wait for streaming response
    const explanation = window.locator('[data-testid="ai-explanation"]');
    await expect(explanation).toBeVisible({ timeout: 3000 });

    // Verify text is streaming (contains partial text)
    const text = await explanation.innerText();
    expect(text.length).toBeGreaterThan(0);
  });
});
```

---

## Test Data Management

### Fixtures

Create reusable test repositories as fixtures:

`tests/e2e/fixtures/repositories.ts`:

```typescript
import path from 'path';
import { execSync } from 'child_process';

export const repositories = {
  small: {
    name: 'test-small',
    files: {
      'main.py': `def greet(): return "Hello"`,
      'utils.py': `def add(a, b): return a + b`,
    },
  },
  large: {
    name: 'test-large',
    files: {
      'src/index.ts': `export function main() {}`,
      'src/types.ts': `export type User = { id: number; name: string };`,
      'tests/index.spec.ts': `describe("main", () => { it("should run", () => {}); });`,
    },
  },
};

export async function seedRepository(repo: typeof repositories.small) {
  const tmpDir = path.join('/tmp', repo.name);
  
  // Create directory
  execSync(`rm -rf ${tmpDir} && mkdir -p ${tmpDir}`);
  
  // Write files
  for (const [filePath, content] of Object.entries(repo.files)) {
    const fullPath = path.join(tmpDir, filePath);
    const dir = path.dirname(fullPath);
    execSync(`mkdir -p ${dir}`);
    require('fs').writeFileSync(fullPath, content);
  }
  
  // Initialize git
  execSync(`cd ${tmpDir} && git init && git config user.email "test@example.com" && git config user.name "Test"`);
  execSync(`cd ${tmpDir} && git add . && git commit -m "Initial"`);
  
  return tmpDir;
}
```

---

## Performance Budgets

E2E tests validate performance constraints:

```typescript
test('should load search results in < 2s', async ({ page }) => {
  const startTime = Date.now();
  
  page.goto('http://localhost:3000/search?q=function');
  await page.locator('[data-testid="search-result"]').first().waitFor();
  
  const duration = Date.now() - startTime;
  expect(duration).toBeLessThan(2000);
});

test('VS Code extension activation < 500ms', async () => {
  const startTime = Date.now();
  // ... launch extension ...
  const duration = Date.now() - startTime;
  expect(duration).toBeLessThan(500);
});
```

---

## CI/CD Integration

### GitLab CI

`.gitlab-ci.yml` (excerpt):

```yaml
e2e_tests:
  stage: test
  script:
    # Install dependencies
    - npm install
    - npx playwright install --with-deps

    # Run tests
    - npx playwright test
  artifacts:
    when: always
    paths:
      - test-results/
      - playwright-report/
    reports:
      junit: test-results.xml
  retry: 1  # Retry once for flaky network
  timeout: 15m
```

### Nightly Test Run

For longer tests (stress tests, large repository scans):

```yaml
e2e_tests_nightly:
  stage: test
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'  # Runs nightly
  script:
    - npx playwright test --grep @slow
  timeout: 60m
```

---

## Debugging Failed Tests

### Run Specific Test

```bash
npx playwright test tests/e2e/vscode-extension/completion.spec.ts
```

### Debug Mode (Interactive)

```bash
npx playwright test --debug

# Opens Playwright Inspector; step through line-by-line
```

### View Traces

```bash
npx playwright show-trace tests/e2e/trace.zip
```

### Video & Screenshot on Failure

Configured in `playwright.config.ts`:
- `screenshot: 'only-on-failure'`
- `video: 'retain-on-failure'`

Check `/test-results/` for artifacts.

---

## Flaky Test Management

If a test fails intermittently:

1. **Identify root cause:** Timing? Race condition? Network?
2. **Increase timeout:** Use `{ timeout: 10000 }` for slow operations.
3. **Retry logic:** Set `retries: 2` in config for CI only.
4. **Or delete it:** If it's not worth the flakiness, remove it.

All flaky tests are labeled with `@flaky` and must be resolved within 5 days.

---

## Manual Testing Checklist (Pre-Release)

Before every release, test on a "large repository" (Linux kernel, React):

- [ ] Extension loads without errors
- [ ] Search returns results in < 2s
- [ ] Code completion triggers on typing
- [ ] Hover info shows documentation
- [ ] AI-generated code samples are streamed correctly
- [ ] No crashes or memory leaks after 1h use

---

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Electron Testing](https://playwright.dev/docs/test-electron)
- [VS Code Extension Testing Guide](https://code.visualstudio.com/api/working-with-extensions/testing-extensions)
