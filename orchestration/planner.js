/**
 * PLANNER - creates a distributed execution plan
 */

import fs from 'fs/promises';
import crypto from 'crypto';

class ExecutionPlanner {
  constructor() {
    this.plan = null;
    this.nodeCounter = 0;
  }

  /**
   * Create execution plan
   */
  async createPlan(analysis, scale) {
    // 1. Split into nodes
    const nodes = await this.createNodes(analysis, scale);

    // 2. Split nodes into tasks
    const tasks = await this.createTasks(nodes);

    // 3. Determine dependencies
    const dependencies = await this.analyzeDependencies(nodes, tasks);

    // 4. Optimize distribution
    const optimized = await this.optimizeDistribution(nodes, tasks, dependencies);

    this.plan = {
      conductor_id: crypto.randomUUID(),
      mission: analysis.goal,
      scale,
      nodes: optimized.nodes,
      tasks: optimized.tasks,
      dependencies: optimized.dependencies,
      estimated_duration: this.estimateDuration(optimized),
      parallelism: this.calculateParallelism(optimized)
    };

    return this.plan;
  }

  /**
   * Create execution nodes
   */
  async createNodes(analysis, scale) {
    const scaleConfig = {
      small: { maxNodes: 3, tasksPerNode: 2 },
      medium: { maxNodes: 10, tasksPerNode: 5 },
      large: { maxNodes: 20, tasksPerNode: 10 },
      massive: { maxNodes: 50, tasksPerNode: 20 }
    };

    const config = scaleConfig[scale];
    const subtasks = analysis.decomposition?.subtasks || [];
    const totalTasks = subtasks.length;
    const nodeCount = Math.min(
      Math.ceil(totalTasks / config.tasksPerNode),
      config.maxNodes
    );

    const nodes = [];

    // Group tasks by type
    const tasksByType = this.groupTasksByType(subtasks);

    // Create nodes for each type
    for (const [type, typeTasks] of Object.entries(tasksByType)) {
      const nodeId = `node_${type}_${++this.nodeCounter}`;

      nodes.push({
        id: nodeId,
        type,
        tasks: typeTasks.map(t => t.id),
        estimated_time: typeTasks.reduce((sum, t) => sum + (t.estimated_time || 5), 0),
        dependencies: []
      });
    }

    return nodes;
  }

  /**
   * Group tasks by type
   */
  groupTasksByType(tasks) {
    const groups = {};

    for (const task of tasks) {
      const type = task.type || 'general';

      if (!groups[type]) {
        groups[type] = [];
      }

      groups[type].push(task);
    }

    return groups;
  }

  /**
   * Create tasks
   */
  async createTasks(nodes) {
    const tasks = [];

    for (const node of nodes) {
      for (const taskId of node.tasks) {
        tasks.push({
          id: taskId,
          node_id: node.id,
          type: node.type,
          status: 'pending',
          result: null
        });
      }
    }

    return tasks;
  }

  /**
   * Analyze dependencies
   */
  async analyzeDependencies(nodes, tasks) {
    const dependencies = [];

    // Simple dependency rules
    const typeOrder = ['config', 'code', 'test', 'docs', 'deploy'];

    for (let i = 0; i < nodes.length; i++) {
      const node = nodes[i];
      const nodeTypeIndex = typeOrder.indexOf(node.type);

      if (nodeTypeIndex > 0) {
        // Depends on previous types
        const dependsOn = nodes
          .filter(n => typeOrder.indexOf(n.type) < nodeTypeIndex)
          .map(n => n.id);

        node.dependencies = dependsOn;

        dependencies.push({
          node: node.id,
          depends_on: dependsOn
        });
      }
    }

    return dependencies;
  }

  /**
   * Optimize distribution
   */
  async optimizeDistribution(nodes, tasks, dependencies) {
    // Balance load
    const balanced = this.balanceLoad(nodes);

    // Maximize parallelism
    const parallel = this.maximizeParallelism(balanced, dependencies);

    return {
      nodes: parallel,
      tasks,
      dependencies
    };
  }

  /**
   * Balance load
   */
  balanceLoad(nodes) {
    // Sort by estimated_time descending
    nodes.sort((a, b) => b.estimated_time - a.estimated_time);
    return nodes;
  }

  /**
   * Maximize parallelism
   */
  maximizeParallelism(nodes, dependencies) {
    // Split into execution levels
    const levels = [];
    const completed = new Set();

    while (completed.size < nodes.length) {
      const level = nodes.filter(node => {
        if (completed.has(node.id)) return false;

        const deps = node.dependencies || [];
        return deps.every(dep => completed.has(dep));
      });

      if (level.length === 0) break;

      levels.push(level);
      level.forEach(node => completed.add(node.id));
    }

    // Add level to each node
    levels.forEach((level, index) => {
      level.forEach(node => {
        node.level = index;
      });
    });

    return nodes;
  }

  /**
   * Estimate duration
   */
  estimateDuration(optimized) {
    const levels = {};

    for (const node of optimized.nodes) {
      const level = node.level || 0;

      if (!levels[level]) {
        levels[level] = 0;
      }

      levels[level] = Math.max(levels[level], node.estimated_time);
    }

    return Object.values(levels).reduce((sum, time) => sum + time, 0);
  }

  /**
   * Calculate parallelism
   */
  calculateParallelism(optimized) {
    const levels = {};

    for (const node of optimized.nodes) {
      const level = node.level || 0;
      levels[level] = (levels[level] || 0) + 1;
    }

    const values = Object.values(levels);
    return values.length > 0 ? Math.max(...values) : 1;
  }
}

// CLI
function parseArg(name) {
  const arg = process.argv.find(a => a.startsWith(`--${name}`));
  if (!arg) return undefined;
  // Support both --name=value and --name value
  if (arg.includes('=')) return arg.split('=').slice(1).join('=');
  const idx = process.argv.indexOf(arg);
  return process.argv[idx + 1];
}

const analysisPath = parseArg('analysis');
const scale = parseArg('scale') || 'medium';
const outputPath = parseArg('output');

if (!analysisPath) {
  console.error('Usage: node planner.js --analysis <path> --scale <small|medium|large|massive> --output <path>');
  process.exit(1);
}

const planner = new ExecutionPlanner();

const analysis = JSON.parse(await fs.readFile(analysisPath, 'utf-8'));
const plan = await planner.createPlan(analysis, scale);

if (outputPath) {
  await fs.writeFile(outputPath, JSON.stringify(plan, null, 2));
} else {
  console.log(JSON.stringify(plan, null, 2));
}
