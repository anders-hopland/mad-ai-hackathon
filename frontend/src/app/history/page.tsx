'use client';

import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import TestRunCard from '@/components/tests/TestRunCard';
import { useTestRuns } from '@/lib/hooks';

export default function HistoryPage() {
  const { data: testRuns, isLoading, error } = useTestRuns();
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filter test runs based on search term
  const filteredTestRuns = testRuns?.filter(testRun => {
    const searchLower = searchTerm.toLowerCase();
    return (
      testRun.url.toLowerCase().includes(searchLower) ||
      testRun.scenario.toLowerCase().includes(searchLower) ||
      testRun.id.toLowerCase().includes(searchLower)
    );
  });
  
  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Test History</h1>
          
          <div className="form-control">
            <input
              type="text"
              placeholder="Search tests..."
              className="input input-bordered w-full max-w-xs"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        ) : error ? (
          <div className="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Error loading test runs. Please try again later.</span>
          </div>
        ) : filteredTestRuns?.length === 0 ? (
          <div className="alert">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-info shrink-0 w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>
              {searchTerm 
                ? "No test runs match your search criteria." 
                : "No test runs found. Start by creating a new test."}
            </span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTestRuns?.map((testRun) => (
              <TestRunCard key={testRun.id} testRun={testRun} />
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
