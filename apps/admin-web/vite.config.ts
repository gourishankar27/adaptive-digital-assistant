import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// Fixed server-side target: a user-entered URL can never redirect the proxy or token.
const target = process.env.ADA_API_TARGET ?? 'http://127.0.0.1:8000';
const url = new URL(target);
if (url.username || url.password || url.search || url.hash || url.pathname !== '/') {
  throw new Error('ADA_API_TARGET must be an origin without credentials or a path.');
}
if (url.protocol !== 'https:' && !(url.protocol === 'http:' && ['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname))) {
  throw new Error('Use HTTPS, or a loopback development API target.');
}

export default defineConfig({
  base: '/admin/',
  plugins: [react()],
  server: {
    host: '127.0.0.1', port: 5173, strictPort: true,
    proxy: { '/v1': { target: url.origin, changeOrigin: false } },
  },
  preview: { host: '127.0.0.1', strictPort: true, proxy: { '/v1': { target: url.origin, changeOrigin: false } } },
  test: {
    environment: 'jsdom', setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.{ts,tsx}'],
  },
});
