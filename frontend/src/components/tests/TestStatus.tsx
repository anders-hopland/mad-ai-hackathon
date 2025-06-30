'use client';

import { TestRun } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Loading from '@/components/ui/Loading';

interface TestStatusProps {
  testRun: TestRun;
  isLoading: boolean;
}

export default function TestStatus({ testRun, isLoading }: TestStatusProps) {
  if (isLoading) {
    return <Loading size="lg" text="Loading test information..." />;
  }

  const formattedDate = new Date(testRun.created_at).toLocaleString();
  
  return (
    <Card className="mb-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold">Test Run</h2>
            {getStatusBadge(testRun.status)}
          </div>
          <div className="flex items-center gap-1 text-sm opacity-70 mt-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {formattedDate}
          </div>
          <div className="flex items-center gap-1 text-sm opacity-70 mt-1">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
            </svg>
            <span className="font-mono">{testRun.id}</span>
          </div>
        </div>
        
        <div className="stats bg-base-200 shadow-sm">
          <div className="stat">
            <div className="stat-figure text-primary">
              {getStatusIcon(testRun.status)}
            </div>
            <div className="stat-title">Status</div>
            <div className="stat-value text-lg">{getStatusText(testRun.status)}</div>
          </div>
        </div>
      </div>
      
      <div className="divider my-4"></div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Target URL
          </h3>
          <div className="mt-2 p-3 bg-base-200 rounded-lg break-all">
            <a href={testRun.url} target="_blank" rel="noopener noreferrer" className="link link-primary">
              {testRun.url}
            </a>
          </div>
        </div>
        <div>
          <h3 className="font-semibold flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Test Scenario
          </h3>
          <div className="mt-2 p-3 bg-base-200 rounded-lg whitespace-pre-wrap">
            {testRun.scenario}
          </div>
        </div>
      </div>
    </Card>
  );
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'completed':
      return <Badge variant="success">Completed</Badge>;
    case 'failed':
      return <Badge variant="error">Failed</Badge>;
    case 'in_progress':
      return <Badge variant="warning">In Progress</Badge>;
    case 'generating_plan':
      return <Badge variant="info">Generating Plan</Badge>;
    case 'executing_tests':
      return <Badge variant="info">Executing Tests</Badge>;
    default:
      return <Badge>{status}</Badge>;
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'in_progress':
      return 'In Progress';
    case 'generating_plan':
      return 'Generating Plan';
    case 'executing_tests':
      return 'Executing Tests';
    case 'completed':
      return 'Completed';
    case 'failed':
      return 'Failed';
    default:
      return status;
  }
}

function getStatusIcon(status: string) {
  const spinnerClasses = "loading loading-spinner loading-sm";
  
  switch (status) {
    case 'in_progress':
    case 'generating_plan':
    case 'executing_tests':
      return <span className={spinnerClasses}></span>;
    case 'completed':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    case 'failed':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    default:
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
  }
}
