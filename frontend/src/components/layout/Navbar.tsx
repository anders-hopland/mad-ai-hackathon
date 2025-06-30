'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth';
import { SignInIcon, SignOutIcon, MoonIcon, SunIcon } from '@phosphor-icons/react';

export default function Navbar() {
  const pathname = usePathname();
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const { user, login, logout, isLoading } = useAuth();
  
  // Initialize theme from localStorage or system preference
  useEffect(() => {
    // Check if user has a saved preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
      // Use system preference as fallback
      const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      setTheme(systemPreference);
      document.documentElement.setAttribute('data-theme', systemPreference);
    }
  }, []);
  
  // Toggle theme function
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };
  
  return (
    <div className="navbar bg-base-100 shadow-md px-4 sm:px-6">
      <div className="navbar-start">
        <div className="dropdown">
          <div tabIndex={0} role="button" className="btn btn-ghost lg:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h8m-8 6h16" />
            </svg>
          </div>
          <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li>
              <Link 
                href="/" 
                className={pathname === '/' ? 'active font-medium' : ''}
              >
                New Test
              </Link>
            </li>
            <li>
              <Link 
                href="/history" 
                className={pathname === '/history' ? 'active font-medium' : ''}
              >
                Test History
              </Link>
            </li>
            <div className="divider my-1"></div>
            {user ? (
              <>
                <li className="px-4 py-1 text-sm text-gray-500">{user.name}</li>
                <li>
                  <button 
                    onClick={logout}
                    className="flex items-center"
                  >
                    <SignOutIcon size={16} className="mr-2" />
                    Logout
                  </button>
                </li>
              </>
            ) : (
              <li>
                <button onClick={login} className="flex items-center">
                  <SignInIcon size={16} className="mr-2" />
                  Login
                </button>
              </li>
            )}
          </ul>
        </div>
        <Link href="/" className="btn btn-ghost text-xl normal-case">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          AutoQA Web
        </Link>
      </div>
      
      <div className="navbar-center hidden lg:flex">
        <ul className="menu menu-horizontal px-1">
          <li>
            <Link 
              href="/" 
              className={`${pathname === '/' ? 'active font-medium' : ''} px-4`}
            >
              New Test
            </Link>
          </li>
          <li>
            <Link 
              href="/history" 
              className={`${pathname === '/history' ? 'active font-medium' : ''} px-4`}
            >
              Test History
            </Link>
          </li>
        </ul>
      </div>
      
      <div className="navbar-end">
        <button 
          className="btn btn-ghost btn-circle mr-2" 
          onClick={toggleTheme}
          aria-label="Toggle theme"
        >
          {theme === 'light' ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          )}
        </button>
        
        {user ? (
          <div className="flex items-center gap-2">
            <span className="hidden md:inline text-sm font-medium">{user.name}</span>
            <button 
              onClick={logout}
              className="btn btn-sm btn-outline"
            >
              <SignOutIcon size={16} className="mr-1" />
              Logout
            </button>
          </div>
        ) : (
          <button onClick={login} className="btn btn-sm btn-primary">
            <SignInIcon size={16} className="mr-1" />
            Login
          </button>
        )}
      </div>
    </div>
  );
}
