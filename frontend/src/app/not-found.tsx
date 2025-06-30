import Link from 'next/link';
import MainLayout from '@/components/layout/MainLayout';

export default function NotFound() {
  return (
    <MainLayout>
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-4">404</h1>
          <h2 className="text-2xl mb-6">Page Not Found</h2>
          <p className="mb-8 max-w-md mx-auto">
            The page you are looking for might have been removed, had its name changed, 
            or is temporarily unavailable.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/" className="btn btn-primary">
              Go to Home
            </Link>
            <Link href="/history" className="btn btn-outline">
              View Test History
            </Link>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
