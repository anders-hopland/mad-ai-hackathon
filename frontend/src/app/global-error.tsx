'use client';

import { useEffect } from 'react';
import ErrorDisplay from '@/components/ui/ErrorDisplay';

interface GlobalErrorProps {
  error: Error;
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Global error:', error);
  }, [error]);

  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            <ErrorDisplay
              title="Something went wrong!"
              message="We're sorry, but something went wrong. Our team has been notified."
              error={error}
              retry={reset}
            />
          </div>
        </div>
      </body>
    </html>
  );
}
