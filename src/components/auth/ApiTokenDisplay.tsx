'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import { CopyIcon, RefreshCwIcon } from 'lucide-react';

export default function ApiTokenDisplay() {
  const { user, regenerateApiToken, isLoading, error } = useAuth();
  const [copied, setCopied] = useState(false);
  const [confirmingRegenerate, setConfirmingRegenerate] = useState(false);
  
  const apiToken = user?.apiToken || '';
  
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(apiToken);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };
  
  const handleRegenerateClick = async () => {
    if (!confirmingRegenerate) {
      setConfirmingRegenerate(true);
      return;
    }
    
    try {
      await regenerateApiToken();
      setConfirmingRegenerate(false);
    } catch (error) {
      // Error handled by the hook
    }
  };
  
  const cancelRegenerate = () => {
    setConfirmingRegenerate(false);
  };
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-4">Your API Token</h3>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">
          Use this token to authenticate your API requests. Include it in the Authorization header:
        </p>
        <div className="bg-gray-100 p-2 rounded font-mono text-sm">
          Authorization: Bearer {apiToken}
        </div>
      </div>
      
      <div className="flex flex-col space-y-3 sm:flex-row sm:space-y-0 sm:space-x-3">
        <button
          onClick={copyToClipboard}
          className="flex items-center justify-center px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
        >
          <CopyIcon size={16} className="mr-2" />
          {copied ? 'Copied!' : 'Copy Token'}
        </button>
        
        {!confirmingRegenerate ? (
          <button
            onClick={handleRegenerateClick}
            disabled={isLoading}
            className="flex items-center justify-center px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors"
          >
            <RefreshCwIcon size={16} className="mr-2" />
            Regenerate Token
          </button>
        ) : (
          <div className="flex space-x-2">
            <button
              onClick={handleRegenerateClick}
              disabled={isLoading}
              className="flex items-center justify-center px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
            >
              {isLoading ? 'Regenerating...' : 'Confirm'}
            </button>
            <button
              onClick={cancelRegenerate}
              className="flex items-center justify-center px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
      
      {confirmingRegenerate && (
        <div className="mt-3 text-sm text-red-600">
          Warning: Regenerating your token will invalidate your current token. Any applications using it will need to be updated.
        </div>
      )}
    </div>
  );
}