import { readFile, writeFile } from 'node:fs/promises';
import openapiTS, { astToString } from 'openapi-typescript';
import ts from 'typescript';

const source = new URL('../../../contracts/openapi.json', import.meta.url);
const destination = new URL('../src/api/generated.ts', import.meta.url);
const output = astToString(await openapiTS(source, {
  transform(schema) {
    if (schema.type === 'integer' && schema.format === 'int64') {
      return ts.factory.createKeywordTypeNode(ts.SyntaxKind.BigIntKeyword);
    }
  },
}));
if (process.argv.includes('--check')) {
  if ((await readFile(destination, 'utf8')).replaceAll('\r\n', '\n') !== output.replaceAll('\r\n', '\n')) {
    throw new Error('Generated DTOs differ from contracts/openapi.json. Run npm run contracts:generate.');
  }
} else {
  await writeFile(destination, output, 'utf8');
}
