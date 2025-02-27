import { User } from './types';
import { v4 as uuidv4 } from 'uuid';

// Simple hash function for password (for demo - in production use bcrypt)
export const hashPassword = (password: string): string => {
  // Create a simple hash
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(16);
};

// Verify password
export const verifyPassword = (password: string, hashedPassword: string): boolean => {
  const passwordHash = hashPassword(password);
  return passwordHash === hashedPassword;
};

// Generate a simple token (for demo purposes)
export const generateToken = (user: User): string => {
  return uuidv4() + '-' + Date.now();
};

// Verify token (simplified for demo)
export const verifyToken = (token: string): { id: string; email: string; apiToken: string } | null => {
  // In a real app, this would validate JWT tokens
  // For now, we'll just check if it's a valid format
  if (token && token.length > 20) {
    // Return a dummy payload - in a real app this would decode the JWT
    return { 
      id: 'dummy-id', 
      email: 'dummy-email',
      apiToken: 'dummy-api-token'
    };
  }
  return null;
};