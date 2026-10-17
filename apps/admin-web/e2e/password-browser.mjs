/* global document, localStorage, sessionStorage, fetch */
// Actual cookie behavior against disposable TLS ADA. Never print credential values.
import assert from 'node:assert/strict';
import { chromium, expect } from '@playwright/test';

const origin = process.env.ADA_BROWSER_ORIGIN;
const browser = await chromium.launch({ args: [`--ignore-certificate-errors-spki-list=${process.env.ADA_TLS_SPKI}`] });
try {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(origin + '/admin/overview');
  await page.getByLabel('Username', { exact: true }).fill('synthetic-admin');
  await page.getByLabel('Password', { exact: true }).fill(process.env.ADA_WEB_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'The backend, at a glance.' })).toBeVisible();
  const first = await context.cookies();
  assert.equal(first.length, 2);
  for (const cookie of first) { assert(cookie.httpOnly && cookie.secure && cookie.sameSite === 'Strict' && cookie.path === '/'); assert.equal(cookie.domain, 'localhost'); }
  assert.equal(await page.evaluate(() => document.cookie), '');
  assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length]), [0, 0]);
  const csrf = await page.evaluate(async () => (await fetch('/v1/auth/browser/refresh', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' })).status);
  assert.equal(csrf, 403);
  await expect.poll(async () => (await context.cookies()).find(c => c.name.endsWith('refresh'))?.value !== first.find(c => c.name.endsWith('refresh')).value, { timeout: 45000, intervals: [1000] }).toBe(true);
  await expect(page.getByRole('heading', { name: 'The backend, at a glance.' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'The backend, at a glance.' })).toBeVisible();
  const renewed = await context.cookies();
  assert(first.find(c => c.name.endsWith('refresh')).value !== renewed.find(c => c.name.endsWith('refresh')).value, 'Refresh must rotate');
  await page.getByRole('button', { name: 'Sign out', exact: true }).click();
  await expect.poll(async () => (await context.cookies()).length).toBe(0);
  assert.equal(await page.evaluate(async () => (await fetch('/v1/me')).status), 401);
  await page.getByLabel('Username', { exact: true }).fill('synthetic-owner');
  await page.getByLabel('Password', { exact: true }).fill(process.env.ADA_WEB_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('Access denied');
  await page.getByLabel('Username', { exact: true }).fill('synthetic-admin');
  await page.getByLabel('Password', { exact: true }).fill(process.env.ADA_WEB_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'The backend, at a glance.' })).toBeVisible();
  const otherTab = await context.newPage();
  await otherTab.goto(origin + '/admin/overview');
  await expect(otherTab.getByRole('heading', { name: 'The backend, at a glance.' })).toBeVisible();
  await otherTab.getByRole('button', { name: 'Sign out', exact: true }).click();
  await expect.poll(async () => (await context.cookies()).length).toBe(0);
  await otherTab.getByLabel('Username', { exact: true }).fill('synthetic-admin-two');
  await otherTab.getByLabel('Password', { exact: true }).fill(process.env.ADA_WEB_TEST_PASSWORD);
  await otherTab.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(otherTab.getByRole('heading', { name: 'The backend, at a glance.' })).toBeVisible();
  await page.getByRole('link', { name: 'Providers', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('account changed');
  await otherTab.close();
  await page.getByLabel('Username', { exact: true }).fill('synthetic-admin');
  await page.getByLabel('Password', { exact: true }).fill(process.env.ADA_WEB_TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Know the configured capacity.' })).toBeVisible();
  await page.getByRole('link', { name: 'Settings', exact: true }).click();
  await page.getByLabel('Current password', { exact: true }).fill(process.env.ADA_WEB_TEST_PASSWORD);
  await page.getByLabel('New password', { exact: true }).fill(process.env.ADA_WEB_TEST_PASSWORD + ' changed');
  await page.getByRole('button', { name: 'Change password and sign out', exact: true }).click();
  await expect.poll(async () => (await context.cookies()).length).toBe(0);
  await context.close();
  console.log('TLS browser: password login, HttpOnly/host-only cookies, CSRF, reopen/rotation, logout and non-admin denial passed.');
} finally { await browser.close(); }
