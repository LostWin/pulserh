import { cn } from '../../lib/utils';

/** Base surface used across the app. */
export default function Card({ className, children, ...props }) {
  return (
    <div className={cn('rounded-xl border border-brand-secondary/10 bg-white shadow-sm', className)} {...props}>
      {children}
    </div>
  );
}

/** Optional header row for a card (icon + title + subtitle + action). */
export function CardHeader({ title, subtitle, action, icon: Icon }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-brand-secondary/10 p-5">
      <div className="flex items-center gap-3">
        {Icon && (
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-brand-light text-brand-secondary">
            <Icon size={18} />
          </div>
        )}
        <div>
          <h3 className="font-semibold text-brand-dark">{title}</h3>
          {subtitle && <p className="text-sm text-brand-secondary/80">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  );
}
