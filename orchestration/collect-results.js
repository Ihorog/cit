/**
 * COLLECT-RESULTS - collects execution results from all nodes
 */

import fs from 'fs/promises';
import path from 'path';

function parseArg(name) {
  const arg = process.argv.find(a => a.startsWith(`--${name}`));
  if (!arg) return undefined;
  if (arg.includes('=')) return arg.split('=').slice(1).join('=');
  const idx = process.argv.indexOf(arg);
  return process.argv[idx + 1];
}

const conductorId = parseArg('conductor-id');
const outputPath = parseArg('output');

if (!conductorId) {
  console.error('Usage: node collect-results.js --conductor-id <id> --output <path>');
  process.exit(1);
}

const results = {
  conductor_id: conductorId,
  collected_at: new Date().toISOString(),
  nodes: [],
  tasks: [],
  summary: {
    total_nodes: 0,
    completed_nodes: 0,
    failed_nodes: 0,
    total_tasks: 0,
    completed_tasks: 0,
    failed_tasks: 0
  }
};

if (outputPath) {
  await fs.writeFile(outputPath, JSON.stringify(results, null, 2));
  console.log(`Results collected to ${outputPath}`);
} else {
  console.log(JSON.stringify(results, null, 2));
}
