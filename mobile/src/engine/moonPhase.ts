const KNOWN_NEW_MOON = new Date('2000-01-06').getTime();
const CYCLE_DAYS = 29.530588853;
const PHASES = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'];

export function getMoonPhase(date: Date): string {
  const elapsed = (date.getTime() - KNOWN_NEW_MOON) / 86400000;
  const phase = ((elapsed % CYCLE_DAYS) + CYCLE_DAYS) % CYCLE_DAYS;
  const index = Math.floor((phase / CYCLE_DAYS) * 8) % 8;
  return PHASES[index];
}
