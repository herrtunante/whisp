import { useStore } from "@/store";
import { useState } from "react";

export const useApiClient = () => {
  const { user, jwtToken, isLoggedIn } = useStore(state => ({
    user: state.user,
    jwtToken: state.jwtToken,
    isLoggedIn: state.isLoggedIn
  }));
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const apiRequest = async <T,>(
    endpoint: string,
    method: string = "GET",
    body?: any,
    useJwt: boolean = true
  ): Promise<T> => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Prepare headers
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      
      // Choose authentication method based on parameters and available tokens
      if (useJwt && isLoggedIn && jwtToken) {
        // Use JWT for auth endpoints
        headers["Authorization"] = `Bearer ${jwtToken}`;
      } else if (user?.apiToken) {
        // Use API token for data endpoints
        headers["Authorization"] = `Bearer ${user.apiToken}`;
      }
      
      // Prepare request options
      const requestOptions: RequestInit = {
        method,
        headers,
      };
      
      // Add body for non-GET requests
      if (method !== "GET" && body) {
        requestOptions.body = JSON.stringify(body);
      }
      
      // Make the request
      const response = await fetch(endpoint, requestOptions);
      
      // Parse response
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || `Request failed with status ${response.status}`);
      }
      
      return data as T;
    } catch (err: any) {
      setError(err.message || "Request failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };
  
  return {
    apiRequest,
    isLoading,
    error,
  };
};