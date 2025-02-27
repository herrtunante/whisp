import { useStore, User } from "@/store";
import { useState } from "react";

interface AuthResponse {
  user: User;
  token: string;
}

export const useAuth = () => {
  const { user, isLoggedIn, login, logout, jwtToken } = useStore(state => ({
    user: state.user,
    isLoggedIn: state.isLoggedIn,
    login: state.login,
    logout: state.logout,
    jwtToken: state.jwtToken
  }));
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const registerUser = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email, password }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || "Registration failed");
      }
      
      login(data.user, data.token);
      return data;
    } catch (err: any) {
      setError(err.message || "Registration failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };
  
  const loginUser = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || "Login failed");
      }
      
      login(data.user, data.token);
      return data;
    } catch (err: any) {
      setError(err.message || "Login failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };
  
  const regenerateApiToken = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch("/api/auth/token/regenerate", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${jwtToken}`,
          "Content-Type": "application/json",
        },
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || "Failed to regenerate API token");
      }
      
      // Update user in store with new API token
      if (user) {
        const updatedUser = { ...user, apiToken: data.apiToken };
        login(updatedUser, jwtToken);
      }
      
      return data.apiToken;
    } catch (err: any) {
      setError(err.message || "Failed to regenerate API token");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };
  
  const logoutUser = () => {
    logout();
  };
  
  return {
    user,
    isLoggedIn,
    isLoading,
    error,
    registerUser,
    loginUser,
    logoutUser,
    regenerateApiToken,
  };
};