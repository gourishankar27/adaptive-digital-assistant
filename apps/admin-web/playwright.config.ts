import { randomBytes } from 'node:crypto';
import { defineConfig, devices } from '@playwright/test';

// Ephemeral synthetic credential is inherited by the disposable server and test workers.
// Never print it or record browser traces/screenshots while entering it.
process.env.ADA_WEB_TEST_TOKEN ??= randomBytes(32).toString('base64url');
const python = process.platform === 'win32' ? '../../.venv/Scripts/python.exe' : '../../.venv/bin/python';

export default defineConfig({
  testDir: './e2e', fullyParallel: false, workers: 1, retries: 0, reporter: 'list',
  use: { baseURL: 'http://127.0.0.1:5173', trace: 'off', screenshot: 'off', video: 'off' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    { command: `"${python}" ../../scripts/client_test_server.py --port 18763`, url: 'http://127.0.0.1:18763/health/live', reuseExistingServer: false, timeout: 60000, stdout: 'ignore', stderr: 'pipe' },
    { command: 'npm run dev', url: 'http://127.0.0.1:5173', reuseExistingServer: false, timeout: 30000, env: { ADA_API_TARGET: 'http://127.0.0.1:18763' } },
  ],
});
