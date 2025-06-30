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
    console.error('Test page error:', error);
  }, [error]);

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto py-8">
        <ErrorDisplay
          title="Error Loading Test"
          message="We couldn't load the test information. Please try again."
          error={error}
          retry={reset}
          backLink="/history"
          backText="View all tests"
        />
      </div>
    </MainLayout>
  );
}
