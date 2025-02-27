'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');
  
  const { loginUser, isLoading, error } = useAuth();
  const router = useRouter();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    
    // Form validation
    if (!email || !password) {
      setFormError('Email and password are required');
      return;
    }
    
    try {
      await loginUser(email, password);
      router.push('/dashboard');
    } catch (error) {
      // Error is handled by the hook
    }
  };
  
  return (
    <div className="max-w-md w-full mx-auto bg-white p-8 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6 text-center">Log In</h2>
      
      {(formError || error) && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {formError || error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="your@email.com"
          />
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="********"
          />
        </div>
        
        <div className="flex items-center justify-between">
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
          >
            {isLoading ? 'Logging in...' : 'Sign In'}
          </button>
        </div>
        
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <a href="/register" className="text-blue-500 hover:text-blue-700">
              Sign up
            </a>
          </p>
        </div>
      </form>
    </div>
  );
}