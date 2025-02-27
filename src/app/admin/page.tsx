'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getSystemStats } from '@/lib/auth/stats';
import { UserStats } from '@/lib/auth/stats';

export default function AdminPage() {
  const { user, isLoggedIn } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<{
    totalUsers: number;
    totalApiCalls: number;
    totalPolygonsProcessed: number;
    userStats: UserStats[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Admin only check - using email for simplicity in this demo
  const isAdmin = user?.email === 'admin@example.com' || user?.email === 'sanchez.paus@gmail.com';
  
  useEffect(() => {
    if (!isLoggedIn) {
      router.push('/login?redirect=/admin');
      return;
    }
    
    if (!isAdmin) {
      router.push('/dashboard');
      return;
    }
    
    try {
      const systemStats = getSystemStats();
      setStats(systemStats);
    } catch (error) {
      console.error('Error fetching system stats:', error);
    } finally {
      setLoading(false);
    }
  }, [isLoggedIn, isAdmin, router]);
  
  if (!isLoggedIn || !isAdmin) {
    return null;
  }
  
  if (loading) {
    return (
      <main className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-semibold mb-6">Admin Dashboard</h1>
        <div className="animate-pulse space-y-4">
          <div className="h-12 bg-gray-300 rounded"></div>
          <div className="h-64 bg-gray-300 rounded"></div>
        </div>
      </main>
    );
  }
  
  if (!stats) {
    return (
      <main className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-semibold mb-6">Admin Dashboard</h1>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-red-500">Error loading system statistics</p>
        </div>
      </main>
    );
  }
  
  return (
    <main className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-semibold mb-6">Admin Dashboard</h1>
      
      {/* System overview */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">System Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <h3 className="text-lg text-gray-500 mb-2">Total Users</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.totalUsers}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <h3 className="text-lg text-gray-500 mb-2">Total API Calls</h3>
            <p className="text-3xl font-bold text-green-600">{stats.totalApiCalls}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <h3 className="text-lg text-gray-500 mb-2">Total Polygons</h3>
            <p className="text-3xl font-bold text-purple-600">{stats.totalPolygonsProcessed}</p>
          </div>
        </div>
      </div>
      
      {/* Users statistics */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">User Statistics</h2>
        <div className="bg-white rounded-lg shadow-md overflow-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">API Calls</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Polygons</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stats.userStats.map((userStat) => (
                <tr key={userStat.user.id}>
                  <td className="px-6 py-4 whitespace-nowrap">{userStat.user.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{userStat.user.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{new Date(userStat.user.createdAt).toLocaleDateString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{userStat.totalApiCalls}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{userStat.totalPolygonsProcessed}</td>
                </tr>
              ))}
              
              {stats.userStats.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">No users found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}