/**
 * REPORT-GENERATOR - generates final mission report in markdown
 */

import fs from 'fs/promises';

function parseArg(name) {
  const arg = process.argv.find(a => a.startsWith(`--${name}`));
  if (!arg) return undefined;
  if (arg.includes('=')) return arg.split('=').slice(1).join('=');
  const idx = process.argv.indexOf(arg);
  return process.argv[idx + 1];
}

async function generateReport(results, format) {
  const summary = results.summary || {};
  const lines = [];

  lines.push('### Execution Summary');
  lines.push('');
  lines.push(`| Metric | Value |`);
  lines.push(`|--------|-------|`);
  lines.push(`| Conductor ID | \`${results.conductor_id}\` |`);
  lines.push(`| Total Nodes | ${summary.total_nodes || 0} |`);
  lines.push(`| Completed Nodes | ${summary.completed_nodes || 0} |`);
  lines.push(`| Failed Nodes | ${summary.failed_nodes || 0} |`);
  lines.push(`| Total Tasks | ${summary.total_tasks || 0} |`);
  lines.push(`| Completed Tasks | ${summary.completed_tasks || 0} |`);
  lines.push(`| Failed Tasks | ${summary.failed_tasks || 0} |`);
  lines.push('');

  if (results.nodes && results.nodes.length > 0) {
    lines.push('### Node Results');
    lines.push('');
    for (const node of results.nodes) {
      lines.push(`- **${node.node_id}**: ${node.status || 'unknown'}`);
    }
    lines.push('');
  }

  lines.push(`> Report generated at ${new Date().toISOString()}`);

  return lines.join('\n');
}

const resultsPath = parseArg('results');
const format = parseArg('format') || 'markdown';
const outputPath = parseArg('output');

if (!resultsPath) {
  console.error('Usage: node report-generator.js --results <path> --format <markdown> --output <path>');
  process.exit(1);
}

const results = JSON.parse(await fs.readFile(resultsPath, 'utf-8'));
const report = await generateReport(results, format);

if (outputPath) {
  await fs.writeFile(outputPath, report);
  console.log(`Report generated: ${outputPath}`);
} else {
  console.log(report);
}
