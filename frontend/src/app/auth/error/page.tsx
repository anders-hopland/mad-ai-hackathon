'use client';

import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

export default function AuthError() {
  const searchParams = useSearchParams();
  const error = searchParams.get('error');

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-error">Authentication Failed</h1>
        <p className="mb-6 text-gray-600">
          {error || 'An error occurred during authentication.'}
        </p>
        <Link href="/" className="btn btn-primary">
          Try Again
        </Link>
      </div>
    </div>
  );
}