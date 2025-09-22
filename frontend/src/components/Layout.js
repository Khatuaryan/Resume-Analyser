import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  Home, 
  Briefcase, 
  Users, 
  FileText, 
  TrendingUp, 
  User, 
  LogOut,
  Menu,
  X,
  Building2,
  UserCheck
} from 'lucide-react';

const Layout = () => {
  const { user, logout, isHR, isCandidate } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Redirect to appropriate dashboard based on role
  useEffect(() => {
    if (user && location.pathname === '/') {
      if (isHR) {
        navigate('/hr', { replace: true });
      } else if (isCandidate) {
        navigate('/candidate', { replace: true });
      }
    }
  }, [user, isHR, isCandidate, location.pathname, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = isHR ? [
    { name: 'Dashboard', href: '/hr', icon: Home },
    { name: 'Job Postings', href: '/hr/jobs', icon: Briefcase },
    { name: 'Candidates', href: '/hr/candidates', icon: Users },
  ] : [
    { name: 'Dashboard', href: '/candidate', icon: Home },
    { name: 'Resume Upload', href: '/candidate/resume', icon: FileText },
    { name: 'Skill Suggestions', href: '/candidate/skills', icon: TrendingUp },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="relative flex w-64 flex-col bg-white shadow-xl">
          <div className="flex h-16 items-center justify-between px-4">
            <h1 className="text-xl font-bold text-gray-900">
              {isHR ? 'HR Portal' : 'Candidate Portal'}
            </h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 px-4 py-4 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive(item.href)
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </a>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
          <div className="flex h-16 items-center px-4">
            <h1 className="text-xl font-bold text-gray-900">
              {isHR ? 'HR Portal' : 'Candidate Portal'}
            </h1>
          </div>
          <nav className="flex-1 px-4 py-4 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive(item.href)
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </a>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1" />
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* User menu */}
              <div className="flex items-center gap-x-4">
                <div className="flex items-center gap-x-2">
                  {isHR ? (
                    <Building2 className="h-5 w-5 text-primary-600" />
                  ) : (
                    <UserCheck className="h-5 w-5 text-primary-600" />
                  )}
                  <span className="text-sm font-medium text-gray-700">
                    {user?.full_name}
                  </span>
                </div>
                <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200" />
                <div className="flex items-center gap-x-4">
                  <a
                    href="/profile"
                    className="text-base font-medium text-gray-700 hover:text-gray-900 flex items-center gap-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
                  >
                    <User className="h-6 w-6" />
                    <span className="hidden sm:block">Profile</span>
                  </a>
                  <button
                    onClick={handleLogout}
                    className="text-base font-medium text-gray-700 hover:text-gray-900 flex items-center gap-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
                  >
                    <LogOut className="h-6 w-6" />
                    <span className="hidden sm:block">Logout</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
