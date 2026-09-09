/** @param {string|null|undefined} iso */
export function exactTime(iso) {
  if (!iso) return 'Not recorded';
  const date = new Date(iso);
  if (!Number.isFinite(date.getTime())) return 'Not recorded';
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: 'short'
  });
}

/** @param {string|null|undefined} iso @param {number} now */
export function stageDuration(iso, now) {
  if (!iso || !Number.isFinite(new Date(iso).getTime())) return 'Time in stage not recorded';
  const minutes = Math.floor(Math.max(0, now - new Date(iso).getTime()) / 60000);
  if (minutes < 1) return 'Less than 1 min in stage';
  if (minutes < 60) return `${minutes} min in stage`;
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h ${minutes % 60}m in stage`;
  return `${Math.floor(minutes / 1440)}d ${Math.floor((minutes % 1440) / 60)}h in stage`;
}
