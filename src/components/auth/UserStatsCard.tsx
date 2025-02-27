'use client';

import { useState, useEffect } from 'react';
import { getUserStats } from '@/lib/auth/stats';
import { ApiStats } from '@/lib/auth/stats';

interface UserStatsCardProps {
  userId: string;
}

export default function UserStatsCard({ userId }: UserStatsCardProps) {
  const [stats, setStats] = useState<ApiStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      try {
        const userStats = getUserStats(userId);
        setStats(userStats);
      } catch (error) {
        console.error('Error fetching user stats:', error);
      } finally {
        setLoading(false);
      }
    }
  }, [userId]);

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">API Usage Statistics</h2>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-300 rounded w-3/4"></div>
          <div className="h-4 bg-gray-300 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">API Usage Statistics</h2>
        <p className="text-gray-500">No stats available</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">API Usage Statistics</h2>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-gray-500">API Calls</p>
          <p className="text-2xl font-bold text-blue-600">{stats.totalApiCalls}</p>
        </div>
        
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-gray-500">Polygons Processed</p>
          <p className="text-2xl font-bold text-green-600">{stats.totalPolygonsProcessed}</p>
        </div>
      </div>
    </div>
  );
}