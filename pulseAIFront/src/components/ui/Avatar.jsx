import { cn, initials } from '../../lib/utils';

const SIZES = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
};

/** Image avatar with a graceful initials fallback. */
export default function Avatar({ name, src, size = 'md', className }) {
  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className={cn('rounded-full object-cover ring-2 ring-white', SIZES[size], className)}
      />
    );
  }
  return (
    <div
      className={cn(
        'grid place-items-center rounded-full bg-gradient-to-br from-brand-light to-brand-secondary font-semibold text-brand-dark ring-2 ring-white',
        SIZES[size],
        className,
      )}
    >
      {initials(name)}
    </div>
  );
}
