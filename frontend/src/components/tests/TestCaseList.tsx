'use client';

import { useState } from 'react';
import { TestCase } from '@/lib/api';

interface TestCaseListProps {
  testCases: TestCase[];
  isLoading: boolean;
  currentTestCase?: string;
  onSelectTestCase: (testCaseId: string) => void;
}

export default function TestCaseList({
  testCases,
  isLoading,
  currentTestCase,
  onSelectTestCase,
}: TestCaseListProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (!testCases || testCases.length === 0) {
    return (
      <div className="alert">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-info shrink-0 w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>No test cases available yet. The test plan is being generated...</span>
      </div>
    );
  }

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">Test Cases</h2>
        <div className="overflow-x-auto">
          <table className="table table-zebra">
            <thead>
              <tr>
                <th>ID</th>
                <th>Description</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {testCases.map((testCase) => (
                <tr 
                  key={testCase.id}
                  className={`cursor-pointer hover:bg-base-200 ${currentTestCase === testCase.id ? 'bg-base-200' : ''}`}
                  onClick={() => onSelectTestCase(testCase.id)}
                >
                  <td>{testCase.id}</td>
                  <td className="max-w-xs truncate">{testCase.description}</td>
                  <td>
                    {getStatusBadge(testCase.status)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'PASS':
      return <div className="badge badge-success">Pass</div>;
    case 'FAIL':
      return <div className="badge badge-error">Fail</div>;
    case 'ERROR':
      return <div className="badge badge-error">Error</div>;
    case 'running':
      return (
        <div className="badge badge-warning gap-1">
          <span className="loading loading-spinner loading-xs"></span>
          Running
        </div>
      );
    default:
      return <div className="badge badge-ghost">Pending</div>;
  }
}
