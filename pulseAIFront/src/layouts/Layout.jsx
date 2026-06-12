import { useState, Suspense } from 'react';
import { Outlet, Navigate, NavLink, useLocation, Link } from 'react-router-dom';
import { LogOut, Menu, X, Settings, HelpCircle, Sun, Moon } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { SIDEBAR_LINKS } from '../config/roles';
import { cn } from '../lib/utils';
import Avatar from '../components/ui/Avatar';
import logo from '../LOGO 512PX.png';

function PageLoader() {
  return (
    <div className="grid h-[60vh] place-items-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-secondary/20 border-t-brand-secondary" />
    </div>
  );
}

function Brand() {
  return (
    <div className="flex items-center justify-center px-4 py-5">
      <img
        src={logo}
        alt="Pulse RH"
        className="w-40 object-contain drop-shadow-md"
      />
    </div>
  );
}

function SidebarContent({ role, links, onLogout, onNavigate, theme, onToggleTheme }) {
  const isDark = theme === 'dark';

  const linkClass = (isActive) => cn(
    'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150',
    isActive
      ? 'bg-brand-secondary text-white shadow-lg shadow-brand-secondary/20'
      : isDark
        ? 'text-white/75 hover:bg-white/8 hover:text-white'
        : 'text-brand-dark/75 hover:bg-brand-secondary/10 hover:text-brand-secondary'
  );

  const bottomBtnClass = cn(
    'flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150',
    isDark
      ? 'text-white/75 hover:bg-white/8 hover:text-white'
      : 'text-brand-dark/75 hover:bg-brand-secondary/10 hover:text-brand-secondary'
  );

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Role section */}
      <div className={cn(
        "mx-3 mb-2 mt-1 rounded-lg px-3 py-2 transition-colors duration-150",
        isDark ? "bg-white/5" : "bg-brand-light"
      )}>
        <div className={cn("text-[10px] font-semibold uppercase tracking-widest", isDark ? "text-white/40" : "text-brand-secondary/60")}>Espace</div>
        <div className={cn("text-sm font-semibold", isDark ? "text-white" : "text-brand-dark")}>{role}</div>
      </div>

      {/* Main nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-2 space-y-0.5">
        {links.map(({ name, path, icon: Icon }) => (
          <NavLink
            key={name}
            to={path}
            onClick={onNavigate}
            className={({ isActive }) => linkClass(isActive)}
          >
            <Icon size={17} />
            <span>{name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom section: Theme Switcher, Settings, Support, Logout */}
      <div className={cn(
        "border-t px-3 py-3 space-y-0.5 transition-colors duration-150",
        isDark ? "border-white/10" : "border-brand-secondary/10"
      )}>
        {/* Theme switcher button (above Settings) */}
        <button
          onClick={onToggleTheme}
          className={bottomBtnClass}
        >
          {isDark ? <Sun size={17} className="text-amber-400" /> : <Moon size={17} className="text-brand-secondary" />}
          <span>Thème : {isDark ? 'Clair' : 'Sombre'}</span>
        </button>

        <Link
          to="#"
          onClick={onNavigate}
          className={bottomBtnClass}
        >
          <Settings size={17} />
          <span>Settings</span>
        </Link>
        <Link
          to="#"
          onClick={onNavigate}
          className={bottomBtnClass}
        >
          <HelpCircle size={17} />
          <span>Support</span>
        </Link>
        <button
          onClick={onLogout}
          className={cn(
            "flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
            isDark ? "text-white/55 hover:bg-white/8 hover:text-white" : "text-brand-dark/55 hover:bg-brand-secondary/10 hover:text-brand-secondary"
          )}
        >
          <LogOut size={17} />
          <span>Déconnexion</span>
        </button>
      </div>
    </div>
  );
}

export default function Layout() {
  const { user, role, logout } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Initialize theme: default to dark sidebar (original style)
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('pulse-theme');
    if (saved === 'dark' || saved === 'light') return saved;
    return 'dark';
  });

  const toggleTheme = () => {
    setTheme(prev => {
      const next = prev === 'dark' ? 'light' : 'dark';
      localStorage.setItem('pulse-theme', next);
      return next;
    });
  };

  if (!user || !role) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const links = SIDEBAR_LINKS[role] || [];
  const title = location.pathname.split('/').filter(Boolean).pop()?.replace(/-/g, ' ') || '';
  const isDark = theme === 'dark';

  return (
    <div className="flex h-screen overflow-hidden bg-brand-light text-brand-dark">

      {/* ── Desktop sidebar ── */}
      <aside className={cn(
        "z-20 hidden w-60 shrink-0 flex-col md:flex transition-all duration-150",
        isDark ? "bg-brand-dark" : "bg-white border-r border-brand-secondary/10"
      )}>
        {/* Logo */}
        <div className={cn("border-b", isDark ? "border-white/10" : "border-brand-secondary/10")}>
          <Brand />
        </div>
        <SidebarContent role={role} links={links} onLogout={logout} theme={theme} onToggleTheme={toggleTheme} />
      </aside>

      {/* ── Mobile drawer ── */}
      <div className={cn('fixed inset-0 z-40 md:hidden', mobileOpen ? '' : 'pointer-events-none')}>
        <div
          className={cn(
            'absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity',
            mobileOpen ? 'opacity-100' : 'opacity-0',
          )}
          onClick={() => setMobileOpen(false)}
        />
        <aside
          className={cn(
            'absolute left-0 top-0 flex h-full w-64 flex-col transition-all duration-300',
            isDark ? "bg-brand-dark" : "bg-white border-r border-brand-secondary/10",
            mobileOpen ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          <div className={cn("flex items-center justify-between border-b", isDark ? "border-white/10" : "border-brand-secondary/10")}>
            <Brand />
            <button
              onClick={() => setMobileOpen(false)}
              className={cn("mr-4", isDark ? "text-white/60 hover:text-white" : "text-brand-secondary/60 hover:text-brand-secondary")}
            >
              <X size={20} />
            </button>
          </div>
          <SidebarContent
            role={role}
            links={links}
            onLogout={logout}
            theme={theme}
            onToggleTheme={toggleTheme}
            onNavigate={() => setMobileOpen(false)}
          />
        </aside>
      </div>

      {/* ── Main column ── */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top header */}
        <header className="z-10 flex h-14 shrink-0 items-center justify-between border-b border-brand-secondary/10 bg-white/80 px-4 shadow-sm backdrop-blur md:px-6">
          <div className="flex items-center gap-3">
            <button
              className="text-brand-secondary/80 hover:text-brand-dark md:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Ouvrir le menu"
            >
              <Menu size={22} />
            </button>
            <div className="text-base font-semibold capitalize text-brand-dark">{title}</div>
          </div>
          <div className="flex items-center gap-3 rounded-full border border-brand-secondary/10 bg-brand-light py-1.5 pl-3 pr-1.5">
            <div className="hidden text-right sm:block">
              <div className="text-sm font-semibold leading-tight text-brand-dark">{user.name}</div>
              <div className="text-xs leading-tight text-brand-secondary/80">{role}</div>
            </div>
            <Avatar name={user.name} src={user.avatar} size="sm" />
          </div>
        </header>

        <main className="relative flex-1 overflow-auto p-4 md:p-8">
          <div className="mx-auto max-w-7xl">
            <Suspense fallback={<PageLoader />}>
              <Outlet />
            </Suspense>
          </div>
        </main>
      </div>
    </div>
  );
}
