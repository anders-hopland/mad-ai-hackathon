'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import TestStatus from '@/components/tests/TestStatus';
import TestCaseList from '@/components/tests/TestCaseList';
import TestCaseDetail from '@/components/tests/TestCaseDetail';
import TerminalOutput from '@/components/tests/TerminalOutput';
import { useTestRun, useTestCases, useTestLogs, useWebSocketUpdates } from '@/lib/hooks';
import { WebSocketClient } from '@/lib/api';

export default function TestResultPage() {
  const params = useParams();
  const testRunId = params.id as string;
  
  const [selectedTestCase, setSelectedTestCase] = useState<string | null>(null);
  const [wsClient, setWsClient] = useState<WebSocketClient | null>(null);
  
  // Fetch data using React Query
  const { 
    data: testRun, 
    isLoading: isLoadingTestRun,
    error: testRunError 
  } = useTestRun(testRunId);
  
  const { 
    data: testCases, 
    isLoading: isLoadingTestCases 
  } = useTestCases(testRunId);
  
  const { 
    data: logs, 
    isLoading: isLoadingLogs 
  } = useTestLogs(testRunId);
  
  // Get WebSocket update handlers
  const {
    handleStatusUpdate,
    handleTestCaseUpdate,
    handleLogUpdate
  } = useWebSocketUpdates(testRunId);
  
  // Set up WebSocket connection
  useEffect(() => {
    if (!wsClient && testRunId) {
      const client = new WebSocketClient(testRunId);
      
      client.addMessageHandler((data) => {
        console.log('WebSocket message:', data);
        
        // Handle different types of updates
        if (data.type === 'status_update') {
          handleStatusUpdate(data);
        } else if (data.type === 'test_case_update') {
          handleTestCaseUpdate(data);
        } else if (data.type === 'log') {
          handleLogUpdate(data);
        }
      });
      
      client.connect();
      setWsClient(client);
      
      return () => {
        client.disconnect();
      };
    }
  }, [testRunId, wsClient, handleStatusUpdate, handleTestCaseUpdate, handleLogUpdate]);
  
  // Select first test case by default when data is loaded
  useEffect(() => {
    if (testCases && testCases.length > 0 && !selectedTestCase) {
      setSelectedTestCase(testCases[0].id);
    }
  }, [testCases, selectedTestCase]);
  
  // Handle test case selection
  const handleSelectTestCase = (testCaseId: string) => {
    setSelectedTestCase(testCaseId);
  };
  
  // Find the selected test case
  const selectedTestCaseData = testCases?.find(tc => tc.id === selectedTestCase);
  
  if (testRunError) {
    return (
      <MainLayout>
        <div className="alert alert-error">
          <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Error loading test run. Please try again later.</span>
        </div>
      </MainLayout>
    );
  }
  
  return (
    <MainLayout>
      {/* Test Status */}
      {testRun && (
        <TestStatus 
          testRun={testRun} 
          isLoading={isLoadingTestRun} 
        />
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="space-y-6">
          {/* Test Cases List */}
          <TestCaseList 
            testCases={testCases || []}
            isLoading={isLoadingTestCases}
            currentTestCase={selectedTestCase || undefined}
            onSelectTestCase={handleSelectTestCase}
          />
          
          {/* Selected Test Case Detail */}
          {selectedTestCaseData && (
            <TestCaseDetail testCase={selectedTestCaseData} />
          )}
        </div>
        
        {/* Terminal Output */}
        <TerminalOutput 
          logs={logs || []}
          isLoading={isLoadingLogs || (testRun?.status !== 'completed' && testRun?.status !== 'failed')}
        />
      </div>
    </MainLayout>
  );
}
