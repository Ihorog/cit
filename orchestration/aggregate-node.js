/**
 * AGGREGATE-NODE - aggregates task results for a single execution node
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

async function listJsonFiles(dir) {
  const files = [];
  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        files.push(...await listJsonFiles(fullPath));
      } else if (entry.name.endsWith('.json')) {
        files.push(fullPath);
      }
    }
  } catch (err) {
    console.error(`Failed to read directory ${dir}: ${err.message}`);
  }
  return files;
}

const conductorId = parseArg('conductor-id');
const nodeId = parseArg('node-id');
const resultsDir = parseArg('results-dir');
const outputPath = parseArg('output');

if (!conductorId || !nodeId) {
  console.error('Usage: node aggregate-node.js --conductor-id <id> --node-id <id> --results-dir <dir> --output <path>');
  process.exit(1);
}

const taskResults = [];

if (resultsDir) {
  const files = await listJsonFiles(resultsDir);
  for (const file of files) {
    try {
      const data = JSON.parse(await fs.readFile(file, 'utf-8'));
      taskResults.push({ file: path.basename(file), ...data });
    } catch (err) {
      console.error(`Failed to parse ${file}: ${err.message}`);
      taskResults.push({ file: path.basename(file), error: 'parse_failed' });
    }
  }
}

const completed = taskResults.filter(t => !t.error).length;
const failed = taskResults.filter(t => t.error).length;

const aggregate = {
  conductor_id: conductorId,
  node_id: nodeId,
  status: failed === 0 ? 'completed' : 'partial',
  tasks_completed: completed,
  tasks_failed: failed,
  results: taskResults,
  aggregated_at: new Date().toISOString()
};

if (outputPath) {
  await fs.writeFile(outputPath, JSON.stringify(aggregate, null, 2));
  console.log(`Node ${nodeId}: ${completed} completed, ${failed} failed`);
} else {
  console.log(JSON.stringify(aggregate, null, 2));
}
