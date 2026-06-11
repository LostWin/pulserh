import { cn } from '../../lib/utils';

/** Slim progress / score bar, clamped to 0–100. */
export default function ProgressBar({ value = 0, className, barClassName, showLabel = false }) {
  const v = Math.max(0, Math.min(100, Math.round(value)));
  return (
    <div className="flex items-center gap-3">
      <div className={cn('h-2 w-full overflow-hidden rounded-full bg-brand-light', className)}>
        <div
          className={cn('h-full rounded-full transition-all duration-500', barClassName || 'bg-brand-secondary')}
          style={{ width: `${v}%` }}
        />
      </div>
      {showLabel && <span className="w-9 shrink-0 text-right text-xs font-semibold text-brand-secondary/80">{v}%</span>}
    </div>
  );
}
