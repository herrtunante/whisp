'use client';

import { useEffect } from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import { useRouter, usePathname } from 'next/navigation';

interface AuthGuardProps {
  children: React.ReactNode;
}

// Paths that don't require authentication
const publicPaths = ['/login', '/register', '/help', '/documentation'];

export default function AuthGuard({ children }: AuthGuardProps) {
  const { isLoggedIn } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  
  const isPublicPath = publicPaths.includes(pathname) || 
                       pathname.startsWith('/documentation/') ||
                       pathname === '/';
  
  useEffect(() => {
    // If not logged in and not on a public path, redirect to login
    if (!isLoggedIn && !isPublicPath) {
      router.push('/login');
    }
    
    // If logged in and on login or register page, redirect to dashboard
    if (isLoggedIn && (pathname === '/login' || pathname === '/register')) {
      router.push('/dashboard');
    }
  }, [isLoggedIn, pathname, router, isPublicPath]);
  
  // If not logged in and on a protected route, don't render children
  if (!isLoggedIn && !isPublicPath) {
    return null;
  }
  
  return <>{children}</>;
}