"""
FastAPI backend for AutoQA Web Application
"""

import os
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    BackgroundTasks,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Depends,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import uvicorn
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

# Import database and CRUD operations
from .database import init_db, get_db, TestRun, TestPlan, TestCase, TestLog, User
from sqlmodel import Session
from . import crud

# Import AutoQA service
from .autoqa_service import AutoQAService

# Import auth
from .auth import (
    Token,
    UserResponse,
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_user_by_google_id,
    create_user,
    exchange_code_for_token,
    get_google_user_info,
    GOOGLE_CLIENT_ID,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# Create FastAPI app
app = FastAPI(
    title="AutoQA Web API",
    description="API for running automated QA tests on websites",
    version="0.1.0",
)

# Configure CORS - set to allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-Requested-With", "Content-Type", "Authorization"],
    expose_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("autoqa-web")


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, test_run_id: str):
        await websocket.accept()
        if test_run_id not in self.active_connections:
            self.active_connections[test_run_id] = []
        self.active_connections[test_run_id].append(websocket)

    def disconnect(self, websocket: WebSocket, test_run_id: str):
        if test_run_id in self.active_connections:
            if websocket in self.active_connections[test_run_id]:
                self.active_connections[test_run_id].remove(websocket)
            if not self.active_connections[test_run_id]:
                del self.active_connections[test_run_id]

    async def broadcast(self, test_run_id: str, message: str):
        """Send a message to all connected clients for a specific test run"""
        if test_run_id in self.active_connections:
            # Create a copy of the connections list to avoid modification during iteration
            connections = self.active_connections[test_run_id].copy()
            closed_connections = []

            for connection in connections:
                try:
                    await connection.send_text(message)
                except RuntimeError as e:
                    # Connection already closed
                    if "Cannot call 'send' once a close message has been sent" in str(
                        e
                    ):
                        logger.warning(
                            f"WebSocket already closed for test run {test_run_id}"
                        )
                        closed_connections.append(connection)
                    else:
                        logger.error(f"Error sending message to WebSocket: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error sending WebSocket message: {e}")
                    closed_connections.append(connection)

            # Remove closed connections
            for connection in closed_connections:
                self.disconnect(connection, test_run_id)

    async def safe_broadcast(
        self, test_run_id: str, message_data: dict, message_type: str = None
    ):
        """
        Safely broadcast a message with error handling

        Args:
            test_run_id: The test run ID
            message_data: Dictionary containing the message data
            message_type: Message type (if not provided in message_data)
        """
        try:
            # Prepare the message
            if (
                isinstance(message_data, dict)
                and "type" not in message_data
                and message_type
            ):
                message = json.dumps({"type": message_type, "data": message_data})
            elif isinstance(message_data, dict) and "type" in message_data:
                message = json.dumps(message_data)
            else:
                message = json.dumps(message_data)

            # Broadcast the message
            await self.broadcast(test_run_id, message)
        except Exception as e:
            logger.error(f"Error in safe_broadcast: {e}")
            # Continue execution even if broadcast fails


manager = ConnectionManager()


# Pydantic models for request/response validation
class TestRunRequest(BaseModel):
    url: HttpUrl
    scenario: str


class TestRunResponse(BaseModel):
    id: str
    url: str
    scenario: str
    status: str
    created_at: datetime


class TestCaseResponse(BaseModel):
    id: str
    description: str
    steps: List[str]
    expected_result: str
    actual_result: Optional[str] = None
    status: str
    notes: Optional[str] = None
    executed_at: Optional[datetime] = None


class TestPlanResponse(BaseModel):
    id: int
    test_run_id: str
    plan: Optional[Dict[str, Any]] = None
    generated_at: datetime


class TestLogResponse(BaseModel):
    id: int
    test_run_id: str
    log_text: str
    timestamp: datetime


# Initialize AutoQA service with WebSocket manager
autoqa_service = None


# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to AutoQA Web API"}


# Auth Routes
@app.get("/auth/google")
async def google_auth():
    """Redirect to Google OAuth"""
    from .auth import GOOGLE_REDIRECT_URI
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        "response_type=code&"
        "scope=openid%20email%20profile&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}"
    )
    print(f"Redirecting to Google OAuth with client ID: {google_auth_url=}")
    return RedirectResponse(google_auth_url)


@app.get("/auth/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for access token
        access_token = await exchange_code_for_token(code)

        # Get user info from Google
        google_user = await get_google_user_info(access_token)

        # Check if user exists
        user = get_user_by_google_id(db, google_user.id)

        if not user:
            # Create new user
            user = create_user(
                db,
                email=google_user.email,
                name=google_user.name,
                google_id=google_user.id,
                picture=google_user.picture,
            )

        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )

        print("succesfully authenticated")
        # Redirect to frontend with token
        return RedirectResponse(f"http://localhost:3000/auth/success?token={jwt_token}")

    except Exception as e:
        return RedirectResponse(f"http://localhost:3000/auth/error?error={str(e)}")


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        picture=current_user.picture,
    )


@app.post("/api/test-runs", response_model=TestRunResponse)
async def create_test_run(
    test_run: TestRunRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new test run with the given URL and scenario.
    The test will be executed in the background.
    """
    # Create test run in database
    db_test_run = crud.create_test_run(
        db, current_user.id, str(test_run.url), test_run.scenario
    )

    # Add the test run to the background tasks
    background_tasks.add_task(
        run_autoqa_test,
        test_run_id=db_test_run.run_id,
        url=str(test_run.url),
        scenario=test_run.scenario,
    )

    return {
        "id": db_test_run.run_id,
        "url": db_test_run.url,
        "scenario": db_test_run.scenario,
        "status": db_test_run.status,
        "created_at": db_test_run.created_at,
    }


@app.get("/api/test-runs", response_model=List[TestRunResponse])
async def list_test_runs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List user's test runs with pagination.
    """
    test_runs = crud.get_user_test_runs(db, current_user.id, skip, limit)
    return [
        {
            "id": tr.run_id,
            "url": tr.url,
            "scenario": tr.scenario,
            "status": tr.status,
            "created_at": tr.created_at,
        }
        for tr in test_runs
    ]


@app.get("/api/test-runs/{test_run_id}", response_model=TestRunResponse)
async def get_test_run(
    test_run_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get details for a specific test run.
    """
    db_test_run = crud.get_test_run(db, test_run_id)
    if not db_test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    # Check if test run belongs to current user
    if db_test_run.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": db_test_run.run_id,
        "url": db_test_run.url,
        "scenario": db_test_run.scenario,
        "status": db_test_run.status,
        "created_at": db_test_run.created_at,
    }


@app.get("/api/test-runs/{test_run_id}/cases", response_model=List[TestCaseResponse])
async def get_test_cases(
    test_run_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get all test cases for a specific test run.
    """
    db_test_run = crud.get_test_run(db, test_run_id)
    if not db_test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    # Check if test run belongs to current user
    if db_test_run.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    test_cases = crud.get_test_cases(db, db_test_run.id)
    return [
        {
            "id": tc.tc_id,
            "description": tc.description,
            "steps": json.loads(tc.steps),
            "expected_result": tc.expected_result,
            "actual_result": tc.actual_result,
            "status": tc.status,
            "notes": tc.notes,
            "executed_at": tc.executed_at,
        }
        for tc in test_cases
    ]


@app.get("/api/test-runs/{test_run_id}/logs", response_model=List[TestLogResponse])
async def get_test_logs(
    test_run_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get all logs for a specific test run.
    """
    db_test_run = crud.get_test_run(db, test_run_id)
    if not db_test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    # Check if test run belongs to current user
    if db_test_run.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    logs = crud.get_test_logs(db, db_test_run.id)
    return [
        {
            "id": log.id,
            "test_run_id": test_run_id,
            "log_text": log.log_text,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


@app.websocket("/ws/test-runs/{test_run_id}")
async def websocket_endpoint(
    websocket: WebSocket, test_run_id: str, db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time updates on test runs.
    Note: WebSocket auth is simplified - in production you'd want token-based auth
    """
    # Check if test run exists
    db_test_run = crud.get_test_run(db, test_run_id)
    if not db_test_run:
        await websocket.close(code=1008, reason="Test run not found")
        return

    # Connect to WebSocket
    await manager.connect(websocket, test_run_id)

    # Send initial status
    await websocket.send_text(
        json.dumps(
            {
                "type": "status_update",
                "data": {
                    "status": db_test_run.status,
                    "message": f"Current status: {db_test_run.status}",
                },
            }
        )
    )

    try:
        while True:
            # Just keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, test_run_id)


# Background task for running AutoQA
async def run_autoqa_test(test_run_id: str, url: str, scenario: str):
    """
    Run the AutoQA test in the background and send updates via WebSocket.
    """
    global autoqa_service

    # Initialize AutoQA service if not already done
    if autoqa_service is None:
        autoqa_service = AutoQAService(manager)
    # get GEMINI_API_KEY from .env file
    load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    # Log gemini api key from .env file
    logger.info(
        "Running AutoQA test for run_id: %s gemini api key: %s",
        test_run_id,
        gemini_api_key,
    )

    # Run the test
    await autoqa_service.run_test(test_run_id, url, scenario)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
