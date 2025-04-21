# API REST simplificada

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import time

# Initialize FastAPI app
app = FastAPI(title="Trading System API", description="API for controlling and monitoring the trading system", version="1.0.0")

# Basic authentication
security = HTTPBasic()

# Logger setup
logging.basicConfig(filename="api_requests.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (simple implementation)
RATE_LIMIT = 10  # Max requests per minute
request_counts = {}

# Models
class TraderControlRequest(BaseModel):
    trader_name: str
    action: str  # "start", "stop", "pause", "resume"

class WebhookEvent(BaseModel):
    event_type: str
    payload: dict

# Dependency for authentication
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    valid_username = "admin"
    valid_password = "password123"
    if credentials.username != valid_username or credentials.password != valid_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username

# Middleware for rate limiting
@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < 60]
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    request_counts[client_ip].append(current_time)
    return await call_next(request)

# Endpoints
@app.get("/status", summary="Get system status", tags=["System"])
async def get_status(username: str = Depends(authenticate)):
    """
    Retrieve the current status of the trading system.
    """
    # Placeholder for actual system status
    status = {"system": "running", "traders": ["BTCTrader", "ETHTrader"]}
    logging.info(f"Status requested by {username}")
    return status

@app.post("/trader/control", summary="Control a trader", tags=["Trader"])
async def control_trader(request: TraderControlRequest, username: str = Depends(authenticate)):
    """
    Start, stop, pause, or resume a trader.
    """
    trader_name = request.trader_name
    action = request.action.lower()

    # Placeholder for actual trader control logic
    if trader_name not in ["BTCTrader", "ETHTrader"]:
        raise HTTPException(status_code=404, detail=f"Trader {trader_name} not found")
    if action not in ["start", "stop", "pause", "resume"]:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")

    logging.info(f"Trader {trader_name} action {action} requested by {username}")
    return {"message": f"Trader {trader_name} {action}ed successfully"}

@app.get("/metrics", summary="Get system metrics", tags=["System"])
async def get_metrics(username: str = Depends(authenticate)):
    """
    Retrieve system metrics such as CPU, memory, and GPU usage.
    """
    # Placeholder for actual metrics
    metrics = {"cpu_usage": 45, "memory_usage": 70, "gpu_usage": 30}
    logging.info(f"Metrics requested by {username}")
    return metrics

@app.post("/webhook", summary="Handle webhook events", tags=["Webhooks"])
async def handle_webhook(event: WebhookEvent, username: str = Depends(authenticate)):
    """
    Handle webhook events for critical notifications.
    """
    logging.info(f"Webhook event received: {event.event_type} by {username}")
    # Placeholder for webhook handling logic
    return {"message": f"Webhook event {event.event_type} processed successfully"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTP exceptions.
    """
    logging.error(f"HTTPException: {exc.detail} for request {request.url}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Custom handler for general exceptions.
    """
    logging.error(f"Exception: {str(exc)} for request {request.url}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
