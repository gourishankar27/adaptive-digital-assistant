import { randomBytes, randomUUID } from 'node:crypto';
import { defineConfig, devices } from '@playwright/test';

// Ephemeral synthetic credential is inherited by the disposable server and test workers.
// Never print it or record browser traces/screenshots while entering it.
process.env.ADA_WEB_TEST_TOKEN ??= randomBytes(32).toString('base64url');
process.env.ADA_WEB_TEST_SECOND_TOKEN ??= randomBytes(32).toString('base64url');
process.env.ADA_WEB_TEST_ORDINARY_TOKEN ??= randomBytes(32).toString('base64url');
process.env.ADA_WEB_TEST_SCHEMA ??= `ada_web_test_${randomUUID().replaceAll('-', '')}`;
const python = process.platform === 'win32' ? '../../.venv/Scripts/python.exe' : '../../.venv/bin/python';

export default defineConfig({
  testDir: './e2e', fullyParallel: false, workers: 1, retries: 0, reporter: 'list',
  globalTeardown: './e2e/cleanup.ts',
  use: { baseURL: 'http://127.0.0.1:5173', trace: 'off', screenshot: 'off', video: 'off' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    { command: `"${python}" ../../scripts/admin_web_test_server.py --port 18763`, url: 'http://127.0.0.1:18763/health/live', reuseExistingServer: false, timeout: 60000, stdout: 'ignore', stderr: 'pipe' },
    { command: process.env.ADA_WEB_BUILD_SMOKE === '1' ? 'npm run preview -- --port 5173' : 'npm run dev', url: 'http://127.0.0.1:5173/admin/', reuseExistingServer: false, timeout: 30000, env: { ADA_API_TARGET: 'http://127.0.0.1:18763' } },
  ],
});
