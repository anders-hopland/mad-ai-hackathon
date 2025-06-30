#!/bin/bash

# Start the backend server
echo "Starting backend server..."
cd "$(dirname "$0")"
uv run run_backend.py &
BACKEND_PID=$!

# Start the frontend server
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Function to handle termination
function cleanup {
  echo "Stopping servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup INT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
