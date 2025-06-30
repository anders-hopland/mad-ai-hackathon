import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api', // Use Next.js rewrites to proxy requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface TestRun {
  id: string;
  url: string;
  scenario: string;
  status: string;
  created_at: string;
}

export interface TestCase {
  id: string;
  description: string;
  steps: string[];
  expected_result: string;
  actual_result?: string;
  status: string;
  notes?: string;
  executed_at?: string;
}

export interface TestLog {
  id: number;
  test_run_id: string;
  log_text: string;
  timestamp: string;
}

// API functions
export const apiClient = {
  // Test runs
  createTestRun: async (url: string, scenario: string): Promise<TestRun> => {
    const response = await api.post('/api/test-runs', { url, scenario });
    return response.data;
  },
  
  getTestRuns: async (): Promise<TestRun[]> => {
    const response = await api.get('/api/test-runs');
    return response.data;
  },
  
  getTestRun: async (id: string): Promise<TestRun> => {
    const response = await api.get(`/api/test-runs/${id}`);
    return response.data;
  },
  
  // Test cases
  getTestCases: async (testRunId: string): Promise<TestCase[]> => {
    const response = await api.get(`/api/test-runs/${testRunId}/cases`);
    return response.data;
  },
  
  // Test logs
  getTestLogs: async (testRunId: string): Promise<TestLog[]> => {
    const response = await api.get(`/api/test-runs/${testRunId}/logs`);
    return response.data;
  },
};

// WebSocket connection for real-time updates
export class WebSocketClient {
  private socket: WebSocket | null = null;
  private messageHandlers: ((data: any) => void)[] = [];
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isConnecting: boolean = false;
  
  constructor(private testRunId: string) {}
  
  connect() {
    if (this.socket || this.isConnecting) return;
    
    this.isConnecting = true;
    
    // Use direct WebSocket connection for now - we can create a proxy later if needed
    const url = `ws://localhost:8000/ws/test-runs/${this.testRunId}`;
    
    try {
      this.socket = new WebSocket(url);
      
      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.messageHandlers.forEach(handler => handler(data));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        this.socket = null;
        this.isConnecting = false;
        
        // Attempt to reconnect after a delay
        if (!this.reconnectTimer) {
          this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.connect();
          }, 3000);
        }
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Don't close here, let the onclose handler deal with reconnection
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.isConnecting = false;
      
      // Attempt to reconnect after a delay
      if (!this.reconnectTimer) {
        this.reconnectTimer = setTimeout(() => {
          this.reconnectTimer = null;
          this.connect();
        }, 3000);
      }
    }
  }
  
  addMessageHandler(handler: (data: any) => void) {
    this.messageHandlers.push(handler);
  }
  
  removeMessageHandler(handler: (data: any) => void) {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
  }
  
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
