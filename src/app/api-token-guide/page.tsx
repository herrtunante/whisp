'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import ApiTokenDisplay from '@/components/auth/ApiTokenDisplay';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ApiTokenGuidePage() {
  const { isLoggedIn } = useAuth();
  const router = useRouter();
  
  useEffect(() => {
    if (!isLoggedIn) {
      router.push('/login?redirect=/api-token-guide');
    }
  }, [isLoggedIn, router]);
  
  if (!isLoggedIn) {
    return null;
  }
  
  return (
    <main className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-semibold mb-6">API Token Guide</h1>
      
      <div className="mb-8">
        <ApiTokenDisplay />
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">How to Use Your API Token</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2">1. Include the token in your API requests</h3>
            <p className="mb-3">
              Add your API token to the Authorization header in all your API requests to Whisp:
            </p>
            <div className="bg-gray-100 p-4 rounded font-mono text-sm code-block">
              <code>
                Authorization: Bearer YOUR_API_TOKEN
              </code>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-2">2. Example using cURL</h3>
            <div className="bg-gray-100 p-4 rounded font-mono text-sm overflow-x-auto code-block">
              <pre>{`curl -X POST https://whisp.openforis.org/api/wkt \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_TOKEN" \\
  -d '{"wkt": "POLYGON((-74.0 40.7, -74.0 40.8, -73.9 40.8, -73.9 40.7, -74.0 40.7))"}'`}</pre>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-2">3. Example using JavaScript/Fetch</h3>
            <div className="bg-gray-100 p-4 rounded font-mono text-sm overflow-x-auto code-block">
              <pre>{`const apiToken = 'YOUR_API_TOKEN';

fetch('https://whisp.openforis.org/api/wkt', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': \`Bearer \${apiToken}\`
  },
  body: JSON.stringify({
    wkt: 'POLYGON((-74.0 40.7, -74.0 40.8, -73.9 40.8, -73.9 40.7, -74.0 40.7))'
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));`}</pre>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium mb-2">4. Example using Python/Requests</h3>
            <div className="bg-gray-100 p-4 rounded font-mono text-sm overflow-x-auto code-block">
              <pre>{`import requests
import json

api_token = 'YOUR_API_TOKEN'
url = 'https://whisp.openforis.org/api/wkt'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_token}'
}

data = {
    'wkt': 'POLYGON((-74.0 40.7, -74.0 40.8, -73.9 40.8, -73.9 40.7, -74.0 40.7))'
}

response = requests.post(url, headers=headers, json=data)
print(response.json())`}</pre>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Security Best Practices</h2>
        
        <ul className="list-disc pl-5 space-y-2">
          <li>Keep your API token secure and confidential.</li>
          <li>Do not expose your token in client-side code or public repositories.</li>
          <li>If you suspect your token has been compromised, regenerate it immediately.</li>
          <li>Use environment variables or secure vaults to store your token in your applications.</li>
          <li>Implement proper error handling in your applications when making API requests.</li>
        </ul>
      </div>
    </main>
  );
}