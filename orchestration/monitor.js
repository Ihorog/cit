/**
 * MONITOR - monitors distributed execution
 */

import { Octokit } from '@octokit/rest';

class ExecutionMonitor {
  constructor() {
    this.octokit = new Octokit({
      auth: process.env.GITHUB_TOKEN
    });

    this.owner = 'Ihorog';
    this.repo = 'cit';
  }

  /**
   * Main monitoring loop
   */
  async monitor(conductorId, totalNodes, totalTasks, timeoutSeconds) {
    const startTime = Date.now();
    const timeout = timeoutSeconds * 1000;

    const state = {
      nodesCompleted: 0,
      nodesFailed: 0,
      tasksCompleted: 0,
      tasksFailed: 0
    };

    while (Date.now() - startTime < timeout) {
      // Check node status
      const nodesStatus = await this.checkNodesStatus(conductorId);

      state.nodesCompleted = nodesStatus.filter(n => n.status === 'completed').length;
      state.nodesFailed = nodesStatus.filter(n => n.status === 'failed').length;

      // Check task status
      const tasksStatus = await this.checkTasksStatus(conductorId);

      state.tasksCompleted = tasksStatus.filter(t => t.status === 'completed').length;
      state.tasksFailed = tasksStatus.filter(t => t.status === 'failed').length;

      // Print progress
      console.log(`Progress: ${state.nodesCompleted}/${totalNodes} nodes, ${state.tasksCompleted}/${totalTasks} tasks`);

      // Check completion
      if (state.nodesCompleted + state.nodesFailed >= totalNodes) {
        console.log('All nodes finished.');
        break;
      }

      // Wait before next check
      await this.sleep(10000); // 10 seconds
    }

    // Timeout
    if (Date.now() - startTime >= timeout) {
      throw new Error('Execution timeout');
    }

    return state;
  }

  /**
   * Check node status via artifacts
   */
  async checkNodesStatus(conductorId) {
    const artifacts = await this.octokit.actions.listArtifactsForRepo({
      owner: this.owner,
      repo: this.repo,
      per_page: 100
    });

    const nodeArtifacts = artifacts.data.artifacts.filter(a =>
      a.name.startsWith('node-')
    );

    const statuses = [];

    for (const artifact of nodeArtifacts) {
      const nodeId = artifact.name.replace('node-', '');

      try {
        await this.octokit.actions.downloadArtifact({
          owner: this.owner,
          repo: this.repo,
          artifact_id: artifact.id,
          archive_format: 'zip'
        });

        statuses.push({
          nodeId,
          status: 'completed'
        });
      } catch (error) {
        statuses.push({
          nodeId,
          status: 'failed',
          error: error.message
        });
      }
    }

    return statuses;
  }

  /**
   * Check task status via artifacts
   */
  async checkTasksStatus(conductorId) {
    const artifacts = await this.octokit.actions.listArtifactsForRepo({
      owner: this.owner,
      repo: this.repo,
      per_page: 100
    });

    const taskArtifacts = artifacts.data.artifacts.filter(a =>
      a.name.startsWith('task-')
    );

    return taskArtifacts.map(a => ({
      taskId: a.name,
      status: 'completed'
    }));
  }

  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// CLI
function parseArg(name) {
  const arg = process.argv.find(a => a.startsWith(`--${name}`));
  if (!arg) return undefined;
  if (arg.includes('=')) return arg.split('=').slice(1).join('=');
  const idx = process.argv.indexOf(arg);
  return process.argv[idx + 1];
}

const conductorId = parseArg('conductor-id');
const totalNodes = parseInt(parseArg('total-nodes') || '0');
const totalTasks = parseInt(parseArg('total-tasks') || '0');
const timeout = parseInt(parseArg('timeout') || '3600');

const monitor = new ExecutionMonitor();
await monitor.monitor(conductorId, totalNodes, totalTasks, timeout);
