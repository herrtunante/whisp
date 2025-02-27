import { v4 as uuidv4 } from 'uuid';
import { User, UserLog } from './types';

// Mock database for server-side API routes
let users: User[] = [];
let logs: UserLog[] = [];

// Initialize with any existing data or leave empty for now
const getItem = <T>(key: string, defaultValue: T): T => {
  if (key === 'whisp_users') return users as unknown as T;
  if (key === 'whisp_logs') return logs as unknown as T;
  return defaultValue;
};

const setItem = <T>(key: string, value: T): void => {
  if (key === 'whisp_users') users = value as unknown as User[];
  if (key === 'whisp_logs') logs = value as unknown as UserLog[];
};

// User functions
export const getAllUsers = (): User[] => {
  return getItem<User[]>('whisp_users', []);
};

export const getUserById = (id: string): User | undefined => {
  const users = getAllUsers();
  return users.find(user => user.id === id);
};

export const getUserByEmail = (email: string): User | undefined => {
  const users = getAllUsers();
  return users.find(user => user.email === email);
};

export const getUserByToken = (token: string): User | undefined => {
  const users = getAllUsers();
  return users.find(user => user.apiToken === token);
};

export const createUser = (userData: Omit<User, 'id' | 'createdAt' | 'apiToken'>): User => {
  const users = getAllUsers();
  
  // Check if user with this email already exists
  if (users.some(user => user.email === userData.email)) {
    throw new Error('User with this email already exists');
  }
  
  // Generate a unique API token
  const apiToken = uuidv4();
  
  const newUser: User = {
    id: uuidv4(),
    ...userData,
    createdAt: new Date().toISOString(),
    apiToken,
  };
  
  users.push(newUser);
  setItem('whisp_users', users);
  
  return newUser;
};

export const updateUser = (id: string, userData: Partial<User>): User => {
  const users = getAllUsers();
  const userIndex = users.findIndex(user => user.id === id);
  
  if (userIndex === -1) {
    throw new Error('User not found');
  }
  
  const updatedUser = { ...users[userIndex], ...userData };
  users[userIndex] = updatedUser;
  
  setItem('whisp_users', users);
  return updatedUser;
};

export const regenerateApiToken = (userId: string): string => {
  const newToken = uuidv4();
  updateUser(userId, { apiToken: newToken });
  return newToken;
};

// Logs functions
export const getAllLogs = (): UserLog[] => {
  return getItem<UserLog[]>('whisp_logs', []);
};

export const getUserLogs = (userId: string): UserLog[] => {
  const logs = getAllLogs();
  return logs.filter(log => log.userId === userId);
};

export const createLog = (logData: Omit<UserLog, 'id' | 'timestamp'>): UserLog => {
  const logs = getAllLogs();
  
  const newLog: UserLog = {
    id: uuidv4(),
    ...logData,
    timestamp: new Date().toISOString(),
  };
  
  logs.push(newLog);
  setItem('whisp_logs', logs);
  
  return newLog;
};