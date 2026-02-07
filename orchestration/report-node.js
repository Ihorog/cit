/**
 * REPORT-NODE - reports node completion to the conductor
 */

import fs from 'fs/promises';

function parseArg(name) {
  const arg = process.argv.find(a => a.startsWith(`--${name}`));
  if (!arg) return undefined;
  if (arg.includes('=')) return arg.split('=').slice(1).join('=');
  const idx = process.argv.indexOf(arg);
  return process.argv[idx + 1];
}

const conductorId = parseArg('conductor-id');
const nodeId = parseArg('node-id');
const resultPath = parseArg('result');

if (!conductorId || !nodeId) {
  console.error('Usage: node report-node.js --conductor-id <id> --node-id <id> --result <path>');
  process.exit(1);
}

let result = null;
if (resultPath) {
  try {
    result = JSON.parse(await fs.readFile(resultPath, 'utf-8'));
  } catch {
    result = { error: `Could not read result file: ${resultPath}` };
  }
}

const report = {
  conductor_id: conductorId,
  node_id: nodeId,
  status: result?.status || 'completed',
  result,
  reported_at: new Date().toISOString()
};

console.log(JSON.stringify(report, null, 2));
