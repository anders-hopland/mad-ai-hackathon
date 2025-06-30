'use client';

import { useEffect, useRef } from 'react';
import { TestLog } from '@/lib/api';

interface TerminalOutputProps {
  logs: TestLog[];
  isLoading: boolean;
  autoScroll?: boolean;
}

export default function TerminalOutput({ 
  logs, 
  isLoading,
  autoScroll = true
}: TerminalOutputProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (autoScroll && terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);
  
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">Terminal Output</h2>
        <div 
          ref={terminalRef}
          className="bg-neutral text-neutral-content font-mono text-sm p-4 rounded-lg h-96 overflow-y-auto"
        >
          {isLoading && logs.length === 0 ? (
            <div className="flex justify-center items-center h-full">
              <span className="loading loading-dots loading-lg"></span>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-4">
              No logs available yet. The test will start soon...
            </div>
          ) : (
            <pre className="whitespace-pre-wrap">
              {logs.map((log, index) => (
                <div key={index} className="mb-1">
                  <span className="text-primary-content opacity-60">[{new Date(log.timestamp).toLocaleTimeString()}]</span> {log.log_text}
                </div>
              ))}
              {isLoading && (
                <div className="inline-block">
                  <span className="loading loading-dots loading-sm"></span>
                </div>
              )}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
