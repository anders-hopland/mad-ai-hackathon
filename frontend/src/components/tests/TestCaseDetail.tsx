'use client';

import { TestCase } from '@/lib/api';

interface TestCaseDetailProps {
  testCase: TestCase;
}

export default function TestCaseDetail({ testCase }: TestCaseDetailProps) {
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <div className="flex justify-between items-center">
          <h2 className="card-title text-xl">{testCase.id}: {testCase.description}</h2>
          <div className="badge badge-lg">
            {getStatusBadge(testCase.status)}
          </div>
        </div>
        
        <div className="divider"></div>
        
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-lg">Steps</h3>
            <ol className="list-decimal list-inside space-y-2 mt-2">
              {testCase.steps.map((step, index) => (
                <li key={index} className="pl-2">{step}</li>
              ))}
            </ol>
          </div>
          
          <div>
            <h3 className="font-semibold text-lg">Expected Result</h3>
            <p className="mt-2 pl-2">{testCase.expected_result}</p>
          </div>
          
          {testCase.actual_result && (
            <div>
              <h3 className="font-semibold text-lg">Actual Result</h3>
              <p className="mt-2 pl-2">{testCase.actual_result}</p>
            </div>
          )}
          
          {testCase.notes && (
            <div>
              <h3 className="font-semibold text-lg">Notes</h3>
              <p className="mt-2 pl-2">{testCase.notes}</p>
            </div>
          )}
          
          {testCase.executed_at && (
            <div className="text-sm text-gray-500 mt-4">
              Executed at: {new Date(testCase.executed_at).toLocaleString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'PASS':
      return <span className="text-success">PASS</span>;
    case 'FAIL':
      return <span className="text-error">FAIL</span>;
    case 'ERROR':
      return <span className="text-error">ERROR</span>;
    case 'running':
      return (
        <span className="text-warning flex items-center gap-1">
          <span className="loading loading-spinner loading-xs"></span>
          RUNNING
        </span>
      );
    default:
      return <span className="text-gray-500">PENDING</span>;
  }
}
