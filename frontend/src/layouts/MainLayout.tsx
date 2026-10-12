import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  Megaphone,
  BarChart3,
  SlidersHorizontal,
  UserCircle,
  Menu,
  X,
  Sparkles,
  Bell,
  Plus,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';
import { cn } from '@/utils/cn';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard, roles: ['admin', 'manager', 'user'] },
  { name: 'AI Copilot Chat', path: '/chat', icon: MessageSquare, roles: ['admin', 'manager', 'user'] },
  { name: 'Campaigns', path: '/campaigns', icon: Megaphone, roles: ['admin', 'manager', 'user'] },
  { name: 'Analytics', path: '/analytics', icon: BarChart3, roles: ['admin', 'manager'] },
  { name: 'Integrations & Settings', path: '/settings', icon: SlidersHorizontal, roles: ['admin'] },
  { name: 'User Profile', path: '/profile', icon: UserCircle, roles: ['admin', 'manager', 'user'] },
];

export const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#F8F8F6] text-[#18181B] flex font-sans antialiased">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Left Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-[#FBFBFA] border-r border-[#E8E8E3] flex flex-col transition-transform duration-200 ease-in-out md:static md:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo and Brand */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-[#E8E8E3]">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#18181B] flex items-center justify-center text-white shadow-sm">
              <Sparkles className="w-4 h-4 text-amber-400" />
            </div>
            <span className="font-bold text-base tracking-tight text-[#18181B]">Marketing AI</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden text-[#71717A] hover:text-[#18181B]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
          {navItems.filter((item) => user && item.roles.includes(user.role)).map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  'flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all',
                  isActive
                    ? 'bg-[#18181B] text-white shadow-sm'
                    : 'text-[#52525B] hover:bg-[#EFEFEA] hover:text-[#18181B]'
                )}
              >
                <Icon
                  className={cn(
                    'w-4 h-4',
                    isActive ? 'text-amber-400' : 'text-[#71717A]'
                  )}
                />
                {item.name}
              </NavLink>
            );
          })}
        </nav>

        {/* User profile & Workspace Status Footer */}
        <div className="p-3.5 border-t border-[#E8E8E3] bg-[#F5F5F0]/60">
          <div className="flex items-center justify-between">
            <NavLink
              to="/profile"
              onClick={() => setSidebarOpen(false)}
              className="flex items-center space-x-2.5 truncate group flex-1"
            >
              <div className="w-8 h-8 rounded-full bg-[#18181B] text-white flex items-center justify-center font-bold text-xs shadow-sm">
                {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="truncate">
                <div className="flex items-center gap-1.5">
                  <p className="text-xs font-bold text-[#18181B] truncate group-hover:text-indigo-600">
                    {user?.full_name || user?.username || 'User'}
                  </p>
                  <span className="text-[9px] font-mono uppercase px-1.5 py-0.2 rounded bg-[#E4E4DC] text-[#52525B] font-semibold">
                    {user?.role?.toUpperCase() || 'MEMBER'}
                  </span>
                </div>
                <p className="text-[10px] text-[#71717A] font-mono mt-0.5">
                  User ID: {user?.id ?? 'Unavailable'}
                </p>
              </div>
            </NavLink>
            <button
              onClick={handleLogout}
              title="Log Out"
              className="p-1.5 rounded-lg text-[#71717A] hover:text-rose-600 hover:bg-rose-50 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <header className="h-16 bg-[#FBFBFA]/90 backdrop-blur-md border-b border-[#E8E8E3] flex items-center justify-between px-4 sm:px-8 sticky top-0 z-30">
          {/* Left Breadcrumb & Mobile toggle */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden text-[#71717A] hover:text-[#18181B] p-1"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2 text-xs text-[#71717A]">
              <span className="italic font-serif text-[#18181B]">Marketing AI</span>
              <span>›</span>
              <span className="font-medium text-[#52525B]">Executive Workspace</span>
            </div>
          </div>

          {/* Right Status & Actions */}
          <div className="flex items-center gap-3">
            {/* Quick Copilot trigger */}
            <button
              onClick={() => navigate('/chat')}
              className="hidden lg:flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#F3F3EE] hover:bg-[#EAEAE4] text-xs text-[#71717A] border border-[#E4E4DC] transition-all hover:text-[#18181B]"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Ask AI Copilot...</span>
              <kbd className="text-[10px] bg-white border border-[#DCDCD4] rounded px-1.5 py-0.5 font-mono text-[#71717A]">
                Copilot
              </kbd>
            </button>

            {/* Configured model indicator */}
            <div className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-[#F3F3EE] text-[#52525B] border border-[#E4E4DC]">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Qwen3:8B
            </div>

            {/* Notification Bell (no fake persistent dot) */}
            <NavLink
              to="/campaigns"
              title="Campaign alerts"
              className="relative p-2 rounded-xl text-[#71717A] hover:text-[#18181B] hover:bg-[#EFEFEA] transition-colors"
            >
              <Bell className="w-4 h-4" />
            </NavLink>

            {/* Primary New Campaign Button */}
            <NavLink
              to="/campaigns"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-[#18181B] hover:bg-[#27272A] text-white text-xs font-semibold rounded-xl transition-all shadow-sm"
            >
              <Plus className="w-3.5 h-3.5 text-amber-400" />
              New Campaign
            </NavLink>

            {/* User Avatar */}
            <NavLink to="/profile" className="hidden sm:block">
              <div className="w-8 h-8 rounded-full bg-[#18181B] text-white flex items-center justify-center font-bold text-xs border border-[#E4E4DC]">
                {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
              </div>
            </NavLink>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
