#!/bin/bash

# Function to handle cleanup
cleanup() {
    echo "Stopping services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT

echo "Starting Job Portal..."

# Start Backend
echo "Starting Backend on port 8000..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi
uvicorn main:app --reload &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend on port 5173..."
cd ../frontend
npm run dev -- --host &
FRONTEND_PID=$!

wait $BACKEND_PID $FRONTEND_PID
