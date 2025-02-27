'use client'

import { useStore } from '@/store';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import Link from 'next/link';

export default function Home() {
  const resetStore = useStore((state) => state.reset);
  const { isLoggedIn } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    // Reset store when landing on home page
    resetStore();
    
    // If logged in, redirect to dashboard
    if (isLoggedIn) {
      router.push('/dashboard');
    }
  }, [isLoggedIn, resetStore, router]);

  return (
    <main className="text-center mx-auto px-4 max-w-4xl py-12">
      <h1 className="text-4xl font-bold mt-8">Welcome to Whisp</h1>
      
      <section className="mt-8">
        <p className="text-xl text-gray-600 leading-relaxed">
          WHISP is a Geo Spatial analysis tool designed to aid in zero-deforestation regulation claims. Upload your WKT or GeoJSON to our API to receive a plot or point based analysis built from carefully selected layers processed via Google Earth Engine.
        </p>
      </section>
      
      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Already a User?</h2>
          <p className="mb-6 text-gray-600">Log in to access your dashboard and API token.</p>
          <Link 
            href="/login" 
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg block w-full text-center"
          >
            Login
          </Link>
        </div>
        
        <div className="bg-white p-8 rounded-lg shadow-md border-2 border-blue-500">
          <h2 className="text-2xl font-semibold mb-4">New to Whisp?</h2>
          <p className="mb-6 text-gray-600">Register now to get your API token and start analyzing data.</p>
          <Link 
            href="/register" 
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg block w-full text-center"
          >
            Create an Account
          </Link>
        </div>
      </div>
      
      <section className="mt-16 bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-6">Why Use Whisp?</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-2">Advanced Analysis</h3>
            <p className="text-gray-600">
              Access powerful geospatial analysis through Google Earth Engine to support zero-deforestation regulation claims.
            </p>
          </div>
          
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-2">Easy Integration</h3>
            <p className="text-gray-600">
              Simple API endpoints for WKT and GeoJSON allow you to integrate Whisp into your existing workflows.
            </p>
          </div>
          
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-2">Comprehensive Data</h3>
            <p className="text-gray-600">
              Get access to carefully selected layers of environmental and deforestation data for your analysis.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
