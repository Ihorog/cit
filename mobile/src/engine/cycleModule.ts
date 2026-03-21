export type CyclePhase = 'menstrual' | 'follicular' | 'ovulation' | 'luteal';

export function getCyclePhase(lastStartDate: string, cycleLength = 28): CyclePhase {
  const start = new Date(lastStartDate).getTime();
  const dayOfCycle = Math.floor((Date.now() - start) / 86400000) % cycleLength;
  if (dayOfCycle < 5)  return 'menstrual';
  if (dayOfCycle < 13) return 'follicular';
  if (dayOfCycle < 16) return 'ovulation';
  return 'luteal';
}
