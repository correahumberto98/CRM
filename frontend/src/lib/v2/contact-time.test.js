import { expect, it } from 'vitest';
import { stageDuration, exactTime } from './contact-time.js';

it('does not invent a stage age for legacy contacts', () => {
  expect(stageDuration(null, Date.now())).toBe('Time in stage not recorded');
  expect(exactTime(null)).toBe('Not recorded');
});
it('measures stage elapsed time across minutes, hours and days', () => {
  const start = '2026-09-09T12:00:00Z';
  const now = Date.parse(start);
  expect(stageDuration(start, now)).toBe('Less than 1 min in stage');
  expect(stageDuration(start, now + 61 * 60000)).toBe('1h 1m in stage');
  expect(stageDuration(start, now + 25 * 3600000)).toBe('1d 1h in stage');
  expect(stageDuration(start, now - 1000)).toBe('Less than 1 min in stage');
});
