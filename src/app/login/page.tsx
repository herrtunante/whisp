'use client';

import { useEffect } from 'react';
import LoginForm from '@/components/auth/LoginForm';
import { useAuth } from '@/lib/hooks/useAuth';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function LoginPage() {
  const { isLoggedIn } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    if (isLoggedIn) {
      router.push('/dashboard');
    }
  }, [isLoggedIn, router]);
  
  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="text-center mb-8">
        <Image
          src="/whisp_logo.svg"
          alt="Whisp Logo"
          width={150}
          height={50}
          className="mx-auto mb-4"
        />
        <h1 className="text-3xl font-semibold text-gray-800">Welcome back to Whisp</h1>
        <p className="text-gray-600 mt-2">
          Log in to access the geospatial analysis tools
        </p>
      </div>
      
      <LoginForm />
    </main>
  );
}