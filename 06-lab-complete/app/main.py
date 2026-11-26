import json
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.auth import verify_api_key
from app.cost_guard import check_budget, record_cost
from app.rate_limiter import check_rate_limit
from app.redis_client import redis_healthy
from utils.mock_llm import ask as llm_ask

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({'time': datetime.now(timezone.utc).isoformat(), 'level': record.levelname, 'message': record.getMessage()}, ensure_ascii=False)

logger = logging.getLogger('agent')
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.handlers = [handler]
logger.setLevel(logging.INFO)
logger.propagate = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting agent')
    yield
    logger.info('Shutdown complete')

app = FastAPI(title='Production AI Agent', lifespan=lifespan)

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/ready')
def ready():
    if not redis_healthy():
        raise HTTPException(status_code=503, detail='Redis unavailable')
    return {'status': 'ready'}

@app.post('/ask')
def ask(body: AskRequest, key: str = Depends(verify_api_key)):
    check_rate_limit(key)
    check_budget()
    answer = llm_ask(body.question)
    cost = record_cost(len(body.question.split()) * 2, len(answer.split()) * 2)
    logger.info('Request completed; estimated cost %.8f', cost)
    return {'question': body.question, 'answer': answer}
