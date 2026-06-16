import { EyeOff, Shield } from 'lucide-react';

import { cn } from '../../lib/utils';

const STYLES = {
  visible: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  masked: 'bg-amber-50 text-amber-700 border-amber-200',
  hidden: 'bg-rose-50 text-rose-700 border-rose-200',
  readonly: 'bg-slate-100 text-slate-700 border-slate-200',
};

const LABELS = {
  visible: 'Visible',
  masked: 'Masqué',
  hidden: 'Caché',
  readonly: 'Lecture seule',
};

export default function FieldVisibilityBadge({ visibility, className = '' }) {
  if (!visibility || visibility === 'visible') return null;
  const Icon = visibility === 'hidden' ? EyeOff : Shield;
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold', STYLES[visibility] || STYLES.visible, className)}>
      <Icon size={10} />
      {LABELS[visibility] || visibility}
    </span>
  );
}
