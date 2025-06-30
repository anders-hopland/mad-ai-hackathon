import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, TestRun, TestCase, TestLog } from './api';

// Query keys
export const queryKeys = {
  testRuns: 'testRuns',
  testRun: (id: string) => ['testRun', id],
  testCases: (testRunId: string) => ['testCases', testRunId],
  testLogs: (testRunId: string) => ['testLogs', testRunId],
};

// Hooks for test runs
export function useTestRuns() {
  return useQuery({
    queryKey: [queryKeys.testRuns],
    queryFn: () => apiClient.getTestRuns(),
  });
}

export function useTestRun(id: string) {
  return useQuery({
    queryKey: queryKeys.testRun(id),
    queryFn: () => apiClient.getTestRun(id),
    enabled: !!id,
  });
}

export function useCreateTestRun() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ url, scenario }: { url: string; scenario: string }) => 
      apiClient.createTestRun(url, scenario),
    onSuccess: (data) => {
      // Invalidate the test runs query to refetch the list
      queryClient.invalidateQueries({ queryKey: [queryKeys.testRuns] });
      // Add the new test run to the cache
      queryClient.setQueryData(queryKeys.testRun(data.id), data);
    },
  });
}

// Hooks for test cases
export function useTestCases(testRunId: string) {
  return useQuery({
    queryKey: queryKeys.testCases(testRunId),
    queryFn: () => apiClient.getTestCases(testRunId),
    enabled: !!testRunId,
  });
}

// Hooks for test logs
export function useTestLogs(testRunId: string) {
  return useQuery({
    queryKey: queryKeys.testLogs(testRunId),
    queryFn: () => apiClient.getTestLogs(testRunId),
    enabled: !!testRunId,
  });
}

// Hook to update cache with WebSocket data
export function useWebSocketUpdates(testRunId: string) {
  const queryClient = useQueryClient();
  
  const handleStatusUpdate = (data: any) => {
    if (data.type === 'status_update') {
      // Update the test run status in the cache
      queryClient.setQueryData<TestRun>(
        queryKeys.testRun(testRunId),
        (oldData) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            status: data.data.status,
          };
        }
      );
    }
  };
  
  const handleTestCaseUpdate = (data: any) => {
    if (data.type === 'test_case_update') {
      // Update the test case in the cache
      queryClient.setQueryData<TestCase[]>(
        queryKeys.testCases(testRunId),
        (oldData) => {
          if (!oldData) return oldData;
          return oldData.map(tc => 
            tc.id === data.data.tc_id
              ? { ...tc, ...data.data }
              : tc
          );
        }
      );
    }
  };
  
  const handleLogUpdate = (data: any) => {
    if (data.type === 'log') {
      // Add the new log to the cache
      queryClient.setQueryData<TestLog[]>(
        queryKeys.testLogs(testRunId),
        (oldData) => {
          if (!oldData) return [data.data];
          return [...oldData, data.data];
        }
      );
    }
  };
  
  return {
    handleStatusUpdate,
    handleTestCaseUpdate,
    handleLogUpdate,
  };
}
