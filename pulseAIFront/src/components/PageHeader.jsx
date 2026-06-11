/** Consistent page title block with an optional actions slot on the right. */
export default function PageHeader({ title, subtitle, children }) {
  return (
    <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-brand-dark">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-brand-secondary/80">{subtitle}</p>}
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </div>
  );
}
