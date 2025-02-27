'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import ApiTokenDisplay from '@/components/auth/ApiTokenDisplay';
import UserStatsCard from '@/components/auth/UserStatsCard';
import SubmitGeometry from '@/components/SubmitGeometry';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { user, isLoggedIn, logoutUser } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    if (!isLoggedIn) {
      router.push('/login');
    }
  }, [isLoggedIn, router]);
  
  if (!user) {
    return null;
  }
  
  return (
    <main className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <div>
          <h1 className="text-3xl font-semibold">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user.name}</p>
        </div>
        <button
          onClick={logoutUser}
          className="mt-4 md:mt-0 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
        >
          Log Out
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Geospatial Analysis</h2>
            <SubmitGeometry />
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Account Information</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p>{user.email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Account Created</p>
                <p>{new Date(user.createdAt).toLocaleDateString()}</p>
              </div>
              {user.lastLogin && (
                <div>
                  <p className="text-sm text-gray-500">Last Login</p>
                  <p>{new Date(user.lastLogin).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>
          
          <UserStatsCard userId={user.id} />
          
          <ApiTokenDisplay />
        </div>
      </div>
    </main>
  );
}