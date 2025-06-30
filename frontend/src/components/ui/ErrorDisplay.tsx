'use client';

import Link from 'next/link';

interface ErrorDisplayProps {
  title?: string;
  message?: string;
  error?: Error;
  retry?: () => void;
  backLink?: string;
  backText?: string;
}

export default function ErrorDisplay({
  title = 'Something went wrong',
  message = 'An error occurred while processing your request.',
  error,
  retry,
  backLink = '/',
  backText = 'Go back home',
}: ErrorDisplayProps) {
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <div className="flex flex-col items-center text-center">
          <div className="text-error mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          
          <h2 className="card-title text-2xl mb-2">{title}</h2>
          <p className="mb-4">{message}</p>
          
          {error && process.env.NODE_ENV !== 'production' && (
            <div className="bg-base-200 p-4 rounded-lg text-left w-full overflow-auto mb-4">
              <p className="font-mono text-sm">{error.message}</p>
              {error.stack && (
                <pre className="text-xs mt-2 opacity-70">{error.stack}</pre>
              )}
            </div>
          )}
          
          <div className="flex flex-col sm:flex-row gap-4 mt-2">
            {retry && (
              <button onClick={retry} className="btn btn-primary">
                Try again
              </button>
            )}
            
            <Link href={backLink} className="btn btn-outline">
              {backText}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
