import { expect, test } from '@playwright/test';
import capabilities from '../../../contracts/fixtures/capabilities-current.json' with { type: 'json' };

test('launches the real browser and supports keyboard navigation, narrow layout and appearance', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'A clear connection. A grounded starting point.' })).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('main')).toBeFocused();
  await page.getByRole('button', { name: 'Connect', exact: true }).click();
  await expect(page.getByRole('alert')).toBeFocused();
  await page.getByLabel('Theme').selectOption('dark');
  await page.getByLabel('Text', { exact: true }).selectOption('large');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole('link', { name: 'Design preview' }).click();
  await expect(page.getByRole('main')).toBeFocused();
  await expect(page.getByLabel('Example field')).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflow).toBe(false);
  await page.getByRole('link', { name: 'Screen map' }).click();
  await expect(page.getByText('Phase 6 · planned').first()).toBeVisible();
});

test('explicit HTTP fixtures cover an invalid credential and escaped account text', async ({ page }) => {
  await page.route('**/v1/me', route => route.fulfill({ status: 401, json: { detail: 'do not display arbitrary private body' } }));
  await page.goto('/');
  await page.getByLabel('Bearer token').fill('synthetic-fixture-token');
  await page.getByRole('button', { name: 'Connect', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('invalid or expired');
  await expect(page.getByRole('alert')).toBeFocused();
  await expect(page.getByLabel('Bearer token')).toHaveValue('');
  await expect(page.getByText('do not display arbitrary private body')).toHaveCount(0);
  await page.unroute('**/v1/me');
  await page.route('**/v1/me', route => route.fulfill({ json: { id: '00000000-0000-0000-0000-000000000001', name: '<script>Fixture account</script>' } }));
  await page.route('**/v1/capabilities', route => route.fulfill({ json: capabilities }));
  await page.getByLabel('Bearer token').fill('synthetic-fixture-token');
  await page.getByRole('button', { name: 'Connect', exact: true }).click();
  await expect(page.getByText('<script>Fixture account</script>')).toBeVisible();
  await expect(page.getByText(/grants no admin role/)).toBeVisible();
  expect(await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length }))).toEqual({ local: 0, session: 0 });
});

test('real HTTP adapter authenticates against a disposable migrated ADA backend', async ({ page }) => {
  const token = process.env.ADA_WEB_TEST_TOKEN;
  if (!token) throw new Error('Disposable server test credential is unavailable.');
  await page.goto('/');
  await page.getByLabel('Bearer token').fill(token);
  await page.getByRole('button', { name: 'Connect', exact: true }).click();
  await expect(page.getByText('Account verified')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Foundation Test' })).toBeVisible();
  await expect(page.getByText('Reported available')).toBeVisible();
  await page.reload();
  await expect(page.getByLabel('Bearer token')).toHaveValue('');
  await expect(page.getByText('Foundation Test')).toHaveCount(0);
});
