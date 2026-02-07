/**
 * DASHBOARD - creates a mission dashboard in markdown
 */

import fs from 'fs/promises';

function parseArg(name) {
  const arg = process.argv.find(a => a.startsWith(`--${name}`));
  if (!arg) return undefined;
  if (arg.includes('=')) return arg.split('=').slice(1).join('=');
  const idx = process.argv.indexOf(arg);
  return process.argv[idx + 1];
}

async function createDashboard(plan) {
  const lines = [];

  lines.push('### Mission Dashboard');
  lines.push('');
  lines.push(`| Property | Value |`);
  lines.push(`|----------|-------|`);
  lines.push(`| Conductor ID | \`${plan.conductor_id}\` |`);
  lines.push(`| Mission | ${plan.mission || 'N/A'} |`);
  lines.push(`| Scale | ${plan.scale || 'N/A'} |`);
  lines.push(`| Nodes | ${(plan.nodes || []).length} |`);
  lines.push(`| Tasks | ${(plan.tasks || []).length} |`);
  lines.push(`| Estimated Duration | ${plan.estimated_duration || 0} min |`);
  lines.push(`| Max Parallelism | ${plan.parallelism || 1} |`);
  lines.push('');

  if (plan.nodes && plan.nodes.length > 0) {
    lines.push('### Execution Nodes');
    lines.push('');
    lines.push('| Node ID | Type | Tasks | Level | Dependencies |');
    lines.push('|---------|------|-------|-------|--------------|');

    for (const node of plan.nodes) {
      const deps = (node.dependencies || []).join(', ') || 'none';
      const taskCount = (node.tasks || []).length;
      lines.push(`| \`${node.id}\` | ${node.type} | ${taskCount} | ${node.level ?? 0} | ${deps} |`);
    }
    lines.push('');
  }

  lines.push(`> Generated at ${new Date().toISOString()}`);

  return lines.join('\n');
}

const planPath = parseArg('plan');
const outputPath = parseArg('output');

if (!planPath) {
  console.error('Usage: node dashboard.js --plan <path> --output <path>');
  process.exit(1);
}

const plan = JSON.parse(await fs.readFile(planPath, 'utf-8'));
const dashboard = await createDashboard(plan);

if (outputPath) {
  await fs.writeFile(outputPath, dashboard);
} else {
  console.log(dashboard);
}
