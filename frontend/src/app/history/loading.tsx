import MainLayout from '@/components/layout/MainLayout';
import Loading from '@/components/ui/Loading';

export default function LoadingPage() {
  return (
    <MainLayout>
      <div className="h-96 flex items-center justify-center">
        <Loading text="Loading test history..." />
      </div>
    </MainLayout>
  );
}
