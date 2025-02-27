export interface User {
  id: string;
  email: string;
  name: string;
  password: string; // Hashed password
  createdAt: string; // ISO string
  apiToken: string;
  lastLogin?: string; // ISO string
}

export interface UserLog {
  id: string;
  userId: string;
  endpoint: string;
  requestData: string;
  responseStatus: number;
  timestamp: string; // ISO string
}

export interface RegisterUserData {
  email: string;
  password: string;
  name: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: Omit<User, 'password'>;
  token: string;
}