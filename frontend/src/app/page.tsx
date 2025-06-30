import MainLayout from '@/components/layout/MainLayout';
import TestForm from '@/components/forms/TestForm';

export default function Home() {
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-4">AutoQA Web</h1>
          <p className="text-xl">Automated QA testing for your websites</p>
        </div>
        
        <TestForm />
      </div>
    </MainLayout>
  );
}
