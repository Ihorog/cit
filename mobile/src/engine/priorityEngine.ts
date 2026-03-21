import { FocusObject } from '../models';

export function calculateFocusScore(obj: FocusObject): number {
  return obj.importance * obj.urgency * obj.timeRelevance * obj.ciAlignment * obj.clarity;
}

export function resolveMainFocus(objects: FocusObject[]): FocusObject | null {
  if (!objects.length) return null;
  let maxObj = objects[0];
  let maxScore = calculateFocusScore(maxObj);
  for (let i = 1; i < objects.length; i++) {
    const score = calculateFocusScore(objects[i]);
    if (score > maxScore) { maxScore = score; maxObj = objects[i]; }
  }
  return maxObj;
}
