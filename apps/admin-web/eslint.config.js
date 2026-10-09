import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import hooks from 'eslint-plugin-react-hooks';

export default tseslint.config(
  { ignores: ['node_modules/**', 'dist/**', 'src/api/generated.ts', 'test-results/**', 'playwright-report/**'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: { globals: { document: 'readonly', window: 'readonly', fetch: 'readonly', AbortController: 'readonly', DOMException: 'readonly', URL: 'readonly', Headers: 'readonly', setTimeout: 'readonly', clearTimeout: 'readonly', process: 'readonly', Request: 'readonly', Response: 'readonly', console: 'readonly' } },
    plugins: { 'react-hooks': hooks },
    rules: {
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'error',
    },
  },
  { files: ['**/*.{js,mjs}'], languageOptions: { globals: { process: 'readonly', console: 'readonly', URL: 'readonly' } } },
);
