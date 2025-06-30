'use client';

import { useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import ErrorDisplay from '@/components/ui/ErrorDisplay';

interface ErrorPageProps {
  error: Error;
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('History page error:', error);
  }, [error]);

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto py-8">
        <ErrorDisplay
          title="Error Loading Test History"
          message="We couldn't load your test history. Please try again."
          error={error}
          retry={reset}
          backLink="/"
          backText="Go to home page"
        />
      </div>
    </MainLayout>
  );
}
