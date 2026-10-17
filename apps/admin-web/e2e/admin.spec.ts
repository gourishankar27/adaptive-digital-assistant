import { expect, test, type Page } from '@playwright/test';
import { fixtureAction, ownerA, ownerB, requestId } from './fixture';
async function signIn(page: Page, credential = process.env.ADA_WEB_TEST_TOKEN) {
  if (!credential) throw new Error('Ephemeral browser credential is unavailable.');
  if (await page.getByLabel('Bearer token', { exact: true }).count() === 0) await page.getByLabel('Advanced: legacy bearer token').check(); await page.getByLabel('Bearer token', { exact: true }).fill(credential); await page.getByRole('button', { name: 'Sign in', exact: true }).click();
}
test('keyboard entry, all palettes/brightness contrast, narrow windows and 200% zoom', async ({ page }) => {
  await page.goto('/admin/overview'); await page.keyboard.press('Tab'); await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused(); await page.keyboard.press('Enter'); await expect(page.getByRole('main')).toBeFocused();
  await page.getByRole('button', { name: 'Sign in', exact: true }).click(); await expect(page.getByRole('alert')).toBeFocused();
  await page.getByRole('link', { name: 'Settings' }).click(); await expect(page.getByRole('main')).toBeFocused();
  await expect(page.getByLabel('Color palette')).toHaveValue('blue');
  for (const palette of ['blue', 'red', 'olive']) for (const mode of ['light', 'dark']) {
    await page.getByLabel('Color palette').selectOption(palette); await page.getByLabel('Brightness').selectOption(mode);
    const contrast = await page.locator('.app').evaluate(element => {
      const css = getComputedStyle(element), color = (key: string) => css.getPropertyValue(key).trim();
      function luminance(hex: string) { const digits = hex.length === 4 ? [...hex.slice(1)].map(char => char + char).join('') : hex.slice(1); const values = digits.match(/../g)!.map(pair => parseInt(pair, 16) / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4); return values[0] * .2126 + values[1] * .7152 + values[2] * .0722; }
      function ratio(a: string, b: string) { const x = luminance(color(a)), y = luminance(color(b)); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
      return { text: ratio('--text', '--surface'), muted: ratio('--muted', '--bg'), button: ratio('--on-primary', '--primary'), boundary: ratio('--line', '--surface'), inputBoundary: ratio('--line', '--bg'), focus: ratio('--primary', '--bg') };
    });
    expect(contrast.text).toBeGreaterThanOrEqual(4.5); expect(contrast.muted).toBeGreaterThanOrEqual(4.5); expect(contrast.button).toBeGreaterThanOrEqual(4.5); expect(contrast.boundary).toBeGreaterThanOrEqual(3); expect(contrast.inputBoundary).toBeGreaterThanOrEqual(3); expect(contrast.focus).toBeGreaterThanOrEqual(3);
  }
  await page.getByLabel('Text size').selectOption('large'); await page.setViewportSize({ width: 390, height: 844 }); expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await page.setViewportSize({ width: 1280, height: 900 }); await page.evaluate(() => { document.body.style.zoom = '2'; }); expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await page.reload(); await expect(page.getByLabel('Color palette')).toHaveValue('olive'); await expect(page.getByLabel('Text size')).toHaveValue('large');
  await page.getByLabel('Brightness').selectOption('system'); await page.emulateMedia({ colorScheme: 'dark' }); await expect(page.locator('.app')).toHaveAttribute('data-theme', 'dark');
});
test('actual PostgreSQL sign-in, provider refusal, server pagination, same UUID owners and legacy detail', async ({ page }) => {
  await page.goto('/admin/overview'); await signIn(page); await expect(page.getByText('Responding', { exact: true })).toBeVisible(); await expect(page.getByText('Unavailable', { exact: true })).toBeVisible();
  const jobs = page.getByRole('table', { name: 'Newest maintenance jobs' });
  await expect(jobs.locator('tbody tr')).toHaveCount(2);
  await expect(jobs.getByText('queued', { exact: true })).toBeVisible();
  await expect(jobs.getByText('completed', { exact: true })).toBeVisible();
  await expect(jobs.getByText('Not recorded', { exact: true })).toBeVisible();
  await expect(jobs).not.toContainText('Synthetic browser verification input.');
  await expect(jobs.locator('th[scope="col"]')).toHaveCount(5);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await page.getByRole('region', { name: 'Maintenance job metadata' }).focus();
  await expect(page.getByRole('region', { name: 'Maintenance job metadata' })).toBeFocused();
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.evaluate(() => { document.body.style.zoom = '2'; });
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await page.evaluate(() => { document.body.style.zoom = ''; });
  await page.getByRole('link', { name: 'Providers', exact: true }).click(); await expect(page.getByText('browser-test-unavailable', { exact: true })).toBeVisible(); await expect(page.getByText('provider_unavailable', { exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Requests', exact: true }).click(); await page.getByLabel('Rows per page').selectOption('10'); await page.getByRole('button', { name: 'Apply filters' }).click(); await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(10);
  await page.getByRole('button', { name: 'Next page' }).click(); await expect(page.getByText('Page 2 · 10 rows per page')).toBeVisible(); await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(5);
  const bounds = new URL(page.url()).searchParams;
  await page.getByRole('button', { name: 'Apply filters' }).click(); await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(10);
  expect(new URL(page.url()).searchParams.get('created_from')).toBe(bounds.get('created_from')); expect(new URL(page.url()).searchParams.get('created_to')).toBe(bounds.get('created_to'));
  await page.getByRole('button', { name: 'Reset filters' }).click(); const shared = page.getByRole('link', { name: `Request: ${requestId}`, exact: true }); await expect(shared).toHaveCount(2);
  await expect(page.locator(`a[href="/admin/requests/${ownerA}/${requestId}"]`)).toHaveCount(1); await page.locator(`a[href="/admin/requests/${ownerB}/${requestId}"]`).click(); await expect(page.getByText(/Not recorded — this legacy request/)).toBeVisible();
  await page.getByRole('link', { name: /Back to requests/ }).click(); await page.locator(`a[href="/admin/requests/${ownerA}/${requestId}"]`).click(); await expect(page.getByText('Trace availability', { exact: true })).toBeVisible(); await expect(page.getByText('0 tokens')).toHaveCount(2);
  await page.getByRole('link', { name: 'Requests', exact: true }).click(); await page.getByLabel('State', { exact: true }).selectOption('failed'); await page.getByRole('button', { name: 'Apply filters' }).click(); await expect(page.getByRole('table').locator('tbody tr')).toHaveCount(1); await page.getByRole('link', { name: /Request: / }).click(); await expect(page.getByText('provider_unavailable', { exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Audit', exact: true }).click(); await expect(page.getByRole('table', { name: 'Audit metadata' })).toBeVisible(); await expect(page.getByRole('cell', { name: 'monitor.request', exact: true }).first()).toBeVisible();
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
  await page.reload(); await expect(page.getByLabel('Password', { exact: true })).toHaveValue(''); await expect(page.getByRole('table')).toHaveCount(0);
});
test('ordinary token denied, local revocation clears detail, logout and account/server switches', async ({ page }) => {
  await page.goto(`/admin/requests/${ownerB}/${requestId}`); await signIn(page, process.env.ADA_WEB_TEST_ORDINARY_TOKEN); await expect(page.getByRole('alert')).toContainText('Access denied'); await expect(page.getByText('Identity & outcome')).toHaveCount(0);
  await signIn(page); await expect(page.getByText('Identity & outcome')).toBeVisible();
  try { fixtureAction('revoke'); await page.getByRole('button', { name: 'Refresh', exact: true }).click(); await expect(page.getByRole('alert')).toContainText('Access denied'); await expect(page.getByText('Identity & outcome')).toHaveCount(0); } finally { fixtureAction('grant'); }
  await signIn(page, process.env.ADA_WEB_TEST_SECOND_TOKEN); await expect(page.getByText(/Operator 00000000-0000-0000-0000-000000000202/)).toBeVisible();
  await page.getByRole('button', { name: 'Sign out', exact: true }).click(); await expect(page.getByText('Identity & outcome')).toHaveCount(0); await page.getByLabel('Browser server origin').fill('http://another-host:8000'); if (await page.getByLabel('Bearer token', { exact: true }).count() === 0) await page.getByLabel('Advanced: legacy bearer token').check(); await page.getByLabel('Bearer token', { exact: true }).fill('synthetic-invalid'); await page.getByRole('button', { name: 'Sign in', exact: true }).click(); await expect(page.getByRole('alert')).toContainText('current browser origin'); await expect(page.getByText(/000000000202/)).toHaveCount(0);
});
test('explicit synthetic database-not-ready sign-in explains migration needs and clears the credential', async ({ page }) => {
  // This interception checks failure wording only; subsequent sign-in uses real PostgreSQL/HTTP.
  let attempts = 0;
  await page.route('**/v1/admin/me', route => { attempts++; return route.fulfill({ status: 503, headers: { 'Retry-After': '3' }, json: { detail: 'database_not_ready', private_diagnostic: 'SYNTHETIC_PRIVATE_DIAGNOSTIC' } }); });
  await page.goto('/admin/overview'); await signIn(page);
  const feedback = page.getByRole('alert'), submit = page.getByRole('button', { name: 'Sign in', exact: true });
  await expect(feedback).toContainText('The backend database is not ready.'); await expect(feedback).toContainText('apply the required migrations'); await expect(feedback).toBeFocused();
  await expect(page.getByText('SYNTHETIC_PRIVATE_DIAGNOSTIC')).toHaveCount(0); await expect(page.getByLabel('Bearer token', { exact: true })).toHaveValue(''); await expect(page.getByRole('table')).toHaveCount(0); await expect(submit).toBeDisabled();
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
  await expect(submit).toBeEnabled({ timeout: 5000 }); expect(attempts).toBe(1);
  await page.unroute('**/v1/admin/me'); await signIn(page); await expect(page.getByText('Responding', { exact: true })).toBeVisible();
});
test('failed refresh stays stale, rate limits wait, direct missing detail and expired access', async ({ page }) => {
  await page.goto('/admin/overview'); await signIn(page); await expect(page.getByText('Responding', { exact: true })).toBeVisible();
  await page.route('**/v1/admin/overview?*', route => route.fulfill({ status: 503, json: { detail: '<script>private-error</script>' } }));
  const refresh = page.getByRole('button', { name: 'Refresh', exact: true }); await refresh.click(); await expect(page.getByText(/Stale data — refresh failed/)).toBeVisible(); await expect(page.getByText('Responding', { exact: true })).toBeVisible(); await expect(refresh).toBeFocused(); await expect(refresh).toBeEnabled(); await expect(page.getByText('<script>private-error</script>')).toHaveCount(0);
  await page.unroute('**/v1/admin/overview?*'); await page.route('**/v1/admin/overview?*', route => route.fulfill({ status: 429, headers: { 'Retry-After': '60' }, json: {} })); await refresh.click(); await expect(refresh).toBeDisabled(); await expect(page.getByText(/Retry available in/)).toBeVisible();
  await page.unroute('**/v1/admin/overview?*'); await page.getByRole('button', { name: 'Sign out', exact: true }).click();
  // New page starts a new in-memory session; direct navigation never carries auth.
  await page.goto(`/admin/requests/${ownerA}/00000000-0000-0000-0000-000000009999`); await signIn(page); await expect(page.getByRole('alert')).toContainText('unavailable'); await expect(page.getByText('Identity & outcome')).toHaveCount(0);
  await page.getByRole('link', { name: 'Overview', exact: true }).click(); await expect(page.getByText('Responding', { exact: true })).toBeVisible(); await page.route('**/v1/admin/overview?*', route => route.fulfill({ status: 401, json: { detail: 'private' } })); await page.getByRole('button', { name: 'Refresh', exact: true }).click(); await expect(page.getByRole('alert')).toContainText('session expired'); await expect(page.getByText('Responding', { exact: true })).toHaveCount(0);
});
test('explicit health fixtures show unknown, degraded and escaped model metadata', async ({ page }) => {
  let scenario = 'unknown';
  await page.route('**/v1/admin/providers', async route => {
    const response = await route.fetch(), data = await response.json();
    data.model = '<script>synthetic-model</script>';
    data.health = { reachability: scenario === 'unknown' ? 'unknown' : 'reachable', model_available: scenario === 'unknown' ? null : false, checked_at: scenario === 'unknown' ? null : 1000, error_code: null, cache_seconds: 30 };
    await route.fulfill({ json: data });
  });
  await page.goto('/admin/providers'); await signIn(page); await expect(page.getByText('Unknown / not measured')).toHaveCount(2); await expect(page.getByText('Not measured', { exact: true })).toBeVisible(); await expect(page.getByText('<script>synthetic-model</script>', { exact: true })).toBeVisible(); expect(await page.getByRole('main').locator('script').count()).toBe(0);
  scenario = 'degraded'; await page.getByRole('button', { name: 'Refresh', exact: true }).click(); await expect(page.getByText('Degraded', { exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Overview', exact: true }).click(); await expect(page.getByText('Responding', { exact: true })).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 }); expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await page.getByRole('link', { name: 'Requests', exact: true }).click(); await expect(page.getByRole('table', { name: 'Request metadata' })).toBeVisible(); await expect(page.locator('th[scope="col"]')).toHaveCount(6);
  await page.getByRole('button', { name: 'Refresh', exact: true }).focus(); await page.keyboard.press('Tab'); await expect(page.getByRole('region', { name: 'Request metadata table' })).toBeFocused(); expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await page.setViewportSize({ width: 1280, height: 900 }); await page.evaluate(() => { document.body.style.zoom = '2'; }); expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
});
