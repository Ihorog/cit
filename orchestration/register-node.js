/**
 * REGISTER-NODE - registers an execution node with the conductor
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
const status = parseArg('status') || 'deployed';

if (!conductorId || !nodeId) {
  console.error('Usage: node register-node.js --conductor-id <id> --node-id <id> --status <status>');
  process.exit(1);
}

const registration = {
  conductor_id: conductorId,
  node_id: nodeId,
  status,
  registered_at: new Date().toISOString()
};

console.log(JSON.stringify(registration, null, 2));
