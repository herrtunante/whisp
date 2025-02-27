import { getAllLogs, getAllUsers, getUserLogs } from './db';
import { User } from './types';

// Structure for API usage statistics
export interface ApiStats {
  totalApiCalls: number;
  totalPolygonsProcessed: number;
}

// Structure for user statistics with API usage
export interface UserStats extends ApiStats {
  user: Omit<User, 'password'>;
}

// Get API usage stats for a specific user
export const getUserStats = (userId: string): ApiStats => {
  const logs = getUserLogs(userId);
  
  // Count all API calls
  const totalApiCalls = logs.length;
  
  // Estimate polygon count by counting WKT requests
  // Note: This is an estimate based on the log data
  const totalPolygonsProcessed = logs.filter(log => 
    log.endpoint === '/api/wkt'
  ).length;
  
  return {
    totalApiCalls,
    totalPolygonsProcessed
  };
};

// Get overall system statistics
export const getSystemStats = (): {
  totalUsers: number;
  totalApiCalls: number;
  totalPolygonsProcessed: number;
  userStats: UserStats[];
} => {
  const users = getAllUsers();
  const logs = getAllLogs();
  
  // Calculate overall statistics
  const totalUsers = users.length;
  const totalApiCalls = logs.length;
  const totalPolygonsProcessed = logs.filter(log => 
    log.endpoint === '/api/wkt'
  ).length;
  
  // Calculate statistics per user
  const userStats: UserStats[] = users.map(user => {
    const { totalApiCalls, totalPolygonsProcessed } = getUserStats(user.id);
    
    // Omit password from user data
    const { password, ...userWithoutPassword } = user;
    
    return {
      user: userWithoutPassword,
      totalApiCalls,
      totalPolygonsProcessed
    };
  });
  
  return {
    totalUsers,
    totalApiCalls,
    totalPolygonsProcessed,
    userStats
  };
};