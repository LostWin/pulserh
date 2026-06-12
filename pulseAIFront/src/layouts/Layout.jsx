import { useState, Suspense } from 'react';
import { Outlet, Navigate, NavLink, useLocation, Link } from 'react-router-dom';
import { LogOut, Menu, X, Settings, HelpCircle } from 'lucide-react';
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

function SidebarContent({ role, links, onLogout, onNavigate }) {
  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Role section */}
      <div className="mx-3 mb-2 mt-1 rounded-lg bg-white/5 px-3 py-2">
        <div className="text-[10px] font-semibold uppercase tracking-widest text-white/40">Espace</div>
        <div className="text-sm font-semibold text-white">{role}</div>
      </div>

      {/* Main nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-2 space-y-0.5">
        {links.map(({ name, path, icon: Icon }) => (
          <NavLink
            key={name}
            to={path}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-brand-secondary text-white shadow-lg shadow-brand-secondary/20'
                  : 'text-white/75 hover:bg-white/8 hover:text-white',
              )
            }
          >
            <Icon size={17} />
            <span>{name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom section: Settings, Support, Logout */}
      <div className="border-t border-white/10 px-3 py-3 space-y-0.5">
        <Link
          to="#"
          onClick={onNavigate}
          className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/75 transition-all hover:bg-white/8 hover:text-white"
        >
          <Settings size={17} />
          <span>Settings</span>
        </Link>
        <Link
          to="#"
          onClick={onNavigate}
          className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/75 transition-all hover:bg-white/8 hover:text-white"
        >
          <HelpCircle size={17} />
          <span>Support</span>
        </Link>
        <button
          onClick={onLogout}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/55 transition-all hover:bg-white/8 hover:text-white"
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

  if (!user || !role) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const links = SIDEBAR_LINKS[role] || [];
  const title = location.pathname.split('/').filter(Boolean).pop()?.replace(/-/g, ' ') || '';

  return (
    <div className="flex h-screen overflow-hidden bg-brand-light text-brand-dark">

      {/* ── Desktop sidebar ── */}
      <aside className="z-20 hidden w-60 shrink-0 flex-col bg-brand-dark md:flex">
        {/* Logo */}
        <div className="border-b border-white/10">
          <Brand />
        </div>
        <SidebarContent role={role} links={links} onLogout={logout} />
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
            'absolute left-0 top-0 flex h-full w-64 flex-col bg-brand-dark transition-transform duration-300',
            mobileOpen ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          <div className="flex items-center justify-between border-b border-white/10">
            <Brand />
            <button
              onClick={() => setMobileOpen(false)}
              className="mr-4 text-white/60 hover:text-white"
            >
              <X size={20} />
            </button>
          </div>
          <SidebarContent
            role={role}
            links={links}
            onLogout={logout}
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
