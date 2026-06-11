import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { cn } from '../../lib/utils';
import Card from './Card';

const ACCENTS = {
  blue: 'from-brand-secondary/80 to-brand-secondary',
  purple: 'from-brand-dark/80 to-brand-dark',
  emerald: 'from-brand-secondary/80 to-brand-secondary',
  amber: 'from-brand-danger/80 to-brand-danger',
  rose: 'from-brand-danger/80 to-brand-danger',
  slate: 'from-brand-dark/60 to-brand-dark',
};

/**
 * KPI card with an accent icon and an optional delta indicator.
 * `invertDelta` flips the good/bad colours (e.g. a rising risk is bad).
 */
export default function StatCard({
  icon: Icon, label, value, suffix, delta, deltaLabel,
  accent = 'blue', invertDelta = false,
}) {
  const positive = delta != null && delta >= 0;
  const good = invertDelta ? !positive : positive;

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-brand-secondary/80">{label}</p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-brand-dark">
            {value}
            {suffix && <span className="text-lg font-semibold text-brand-secondary/70">{suffix}</span>}
          </p>
        </div>
        <div className={cn('grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-gradient-to-br text-white shadow-lg', ACCENTS[accent])}>
          {Icon && <Icon size={20} />}
        </div>
      </div>
      {delta != null && (
        <div className="mt-3 flex items-center gap-1.5 text-sm">
          <span className={cn('inline-flex items-center gap-0.5 font-semibold', good ? 'text-brand-secondary' : 'text-brand-danger')}>
            {positive ? <ArrowUpRight size={15} /> : <ArrowDownRight size={15} />}
            {Math.abs(delta)}%
          </span>
          <span className="text-brand-secondary/70">{deltaLabel || 'vs mois dernier'}</span>
        </div>
      )}
    </Card>
  );
}
