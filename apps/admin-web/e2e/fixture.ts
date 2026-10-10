import { spawnSync } from 'node:child_process';
export const ownerA = '00000000-0000-0000-0000-000000000101', ownerB = '00000000-0000-0000-0000-000000000102', requestId = '00000000-0000-0000-0000-000000000010';
export function fixtureAction(action: 'grant' | 'revoke' | 'cleanup') {
  const python = process.platform === 'win32' ? '../../.venv/Scripts/python.exe' : '../../.venv/bin/python';
  const result = spawnSync(python, ['../../scripts/admin_web_test_server.py', '--action', action], { env: process.env, timeout: 15000, stdio: 'ignore', windowsHide: true });
  if (result.status !== 0) throw new Error('Disposable PostgreSQL fixture action failed.');
}
