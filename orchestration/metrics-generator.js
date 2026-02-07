/**
 * METRICS-GENERATOR - generates execution metrics JSON
 */

import fs from 'fs/promises';

function parseArg(name) {
  const arg = process.argv.find(a => a.startsWith(`--${name}`));
  if (!arg) return undefined;
  if (arg.includes('=')) return arg.split('=').slice(1).join('=');
  const idx = process.argv.indexOf(arg);
  return process.argv[idx + 1];
}

async function generateMetrics(results) {
  const summary = results.summary || {};
  const totalNodes = summary.total_nodes || 0;
  const completedNodes = summary.completed_nodes || 0;
  const totalTasks = summary.total_tasks || 0;
  const completedTasks = summary.completed_tasks || 0;

  return {
    conductor_id: results.conductor_id,
    generated_at: new Date().toISOString(),
    node_success_rate: totalNodes > 0 ? completedNodes / totalNodes : 0,
    task_success_rate: totalTasks > 0 ? completedTasks / totalTasks : 0,
    total_nodes: totalNodes,
    total_tasks: totalTasks,
    completed_nodes: completedNodes,
    completed_tasks: completedTasks,
    failed_nodes: summary.failed_nodes || 0,
    failed_tasks: summary.failed_tasks || 0
  };
}

const resultsPath = parseArg('results');
const outputPath = parseArg('output');

if (!resultsPath) {
  console.error('Usage: node metrics-generator.js --results <path> --output <path>');
  process.exit(1);
}

const results = JSON.parse(await fs.readFile(resultsPath, 'utf-8'));
const metrics = await generateMetrics(results);

if (outputPath) {
  await fs.writeFile(outputPath, JSON.stringify(metrics, null, 2));
  console.log(`Metrics generated: ${outputPath}`);
} else {
  console.log(JSON.stringify(metrics, null, 2));
}
