import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Merge Tailwind classes safely (conditional + conflict resolution). */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/** Shared visual language for engagement-risk levels across the whole app. */
export function riskMeta(level) {
  switch (level) {
    case 'high':
      return { label: 'À risque', badge: 'danger', dot: 'bg-brand-danger', text: 'text-brand-danger', soft: 'bg-brand-danger/10' };
    case 'medium':
      return { label: 'À surveiller', badge: 'warning', dot: 'bg-brand-danger', text: 'text-brand-danger', soft: 'bg-brand-danger/10' };
    default:
      return { label: 'Engagé', badge: 'success', dot: 'bg-brand-secondary', text: 'text-brand-secondary', soft: 'bg-brand-light' };
  }
}

/** Text colour for an engagement score (0–100). */
export function engagementText(score) {
  if (score >= 75) return 'text-brand-secondary';
  if (score >= 60) return 'text-brand-secondary/80';
  return 'text-brand-danger';
}

/** Bar/fill colour for an engagement score (0–100). */
export function engagementBar(score) {
  if (score >= 75) return 'bg-brand-secondary';
  if (score >= 60) return 'bg-brand-secondary/70';
  return 'bg-brand-danger';
}

/** Two-letter initials from a full name, used as an avatar fallback. */
export function initials(name = '') {
  return name
    .trim()
    .split(/\s+/)
    .map((n) => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}
