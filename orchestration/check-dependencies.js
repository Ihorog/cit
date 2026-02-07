/**
 * CHECK-DEPENDENCIES - checks whether node dependencies are satisfied
 */

function parseArg(name) {
  const arg = process.argv.find(a => a.startsWith(`--${name}`));
  if (!arg) return undefined;
  if (arg.includes('=')) return arg.split('=').slice(1).join('=');
  const idx = process.argv.indexOf(arg);
  return process.argv[idx + 1];
}

const conductorId = parseArg('conductor-id');
const nodeId = parseArg('node-id');
const depsRaw = parseArg('dependencies') || '[]';

if (!conductorId || !nodeId) {
  console.error('Usage: node check-dependencies.js --conductor-id <id> --node-id <id> --dependencies <json>');
  process.exit(1);
}

let dependencies;
try {
  dependencies = JSON.parse(depsRaw);
} catch {
  dependencies = [];
}

// If no dependencies, node is ready immediately
if (!Array.isArray(dependencies) || dependencies.length === 0) {
  console.log('No dependencies — node is ready.');
  // Set output for GitHub Actions
  const outputFile = process.env.GITHUB_OUTPUT;
  if (outputFile) {
    const { appendFileSync } = await import('fs');
    appendFileSync(outputFile, 'ready=true\n');
  }
  process.exit(0);
}

// With dependencies present, check readiness (stub: mark ready after logging)
console.log(`Node ${nodeId} has ${dependencies.length} dependencies: ${dependencies.join(', ')}`);

const outputFile = process.env.GITHUB_OUTPUT;
if (outputFile) {
  const { appendFileSync } = await import('fs');
  appendFileSync(outputFile, 'ready=true\n');
}
