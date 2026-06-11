import { cn } from '../../lib/utils';

const VARIANTS = {
  success: 'bg-brand-light text-brand-secondary ring-brand-secondary/20',
  warning: 'bg-brand-danger/10 text-brand-danger ring-brand-danger/20',
  danger: 'bg-brand-danger/10 text-brand-danger ring-brand-danger/20',
  info: 'bg-brand-light text-brand-secondary ring-brand-secondary/20',
  purple: 'bg-brand-light text-brand-secondary ring-brand-secondary/20',
  neutral: 'bg-brand-light text-brand-secondary ring-brand-secondary/20',
};

const DOTS = {
  success: 'bg-brand-secondary',
  warning: 'bg-brand-danger',
  danger: 'bg-brand-danger',
  info: 'bg-brand-secondary',
  purple: 'bg-brand-secondary',
  neutral: 'bg-brand-secondary/60',
};

export default function Badge({ variant = 'neutral', dot = false, className, children }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset',
        VARIANTS[variant],
        className,
      )}
    >
      {dot && <span className={cn('h-1.5 w-1.5 rounded-full', DOTS[variant])} />}
      {children}
    </span>
  );
}
