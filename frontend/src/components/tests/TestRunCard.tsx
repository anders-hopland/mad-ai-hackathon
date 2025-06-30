'use client';

import Link from 'next/link';
import { TestRun } from '@/lib/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';

interface TestRunCardProps {
  testRun: TestRun;
}

export default function TestRunCard({ testRun }: TestRunCardProps) {
  const formattedDate = new Date(testRun.created_at).toLocaleString();
  const domain = testRun.url.replace(/^https?:\/\//, '').split('/')[0];
  
  return (
    <Card
      className="hover:shadow-lg transition-all duration-300 h-full"
      title={
        <div className="flex justify-between items-center w-full">
          <span className="truncate">{domain}</span>
          {getStatusBadge(testRun.status)}
        </div>
      }
      subtitle={
        <div className="flex items-center gap-1 text-xs mt-1">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {formattedDate}
        </div>
      }
      footer={
        <Link href={`/tests/${testRun.id}`} className="btn btn-primary btn-sm w-full">
          View Details
        </Link>
      }
      compact
    >
      <p className="line-clamp-2 text-sm">{testRun.scenario}</p>
    </Card>
  );
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'completed':
      return <Badge variant="success" size="sm">Completed</Badge>;
    case 'failed':
      return <Badge variant="error" size="sm">Failed</Badge>;
    case 'in_progress':
    case 'generating_plan':
    case 'executing_tests':
      return (
        <Badge variant="warning" size="sm" className="flex items-center gap-1">
          <span className="loading loading-spinner loading-xs"></span>
          In Progress
        </Badge>
      );
    default:
      return <Badge size="sm">{status}</Badge>;
  }
}
