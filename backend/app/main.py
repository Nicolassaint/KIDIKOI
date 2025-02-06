from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from asyncio import TimeoutError
import asyncio
from fastapi.responses import JSONResponse
from .api.endpoints import router
from dotenv import load_dotenv

load_dotenv()


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout=300):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except TimeoutError:
            return JSONResponse({"detail": "Request timeout"}, status_code=504)


app = FastAPI(title="Audio Transcription API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add timeout middleware
app.add_middleware(TimeoutMiddleware, timeout=600)  # 10 minutes par exemple

app.include_router(router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Documentation de l'API présente sur la route /docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8502)
