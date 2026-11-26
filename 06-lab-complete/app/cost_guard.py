from datetime import datetime, timezone
from fastapi import HTTPException
from app.config import settings
from app.redis_client import r

PRICE_INPUT_PER_1K = 0.00015
PRICE_OUTPUT_PER_1K = 0.0006

def _key():
    return 'cost:' + datetime.now(timezone.utc).strftime('%Y-%m-%d')

def check_budget() -> None:
    if float(r.get(_key()) or 0) >= settings.daily_budget_usd:
        raise HTTPException(status_code=402, detail='Daily budget exceeded')

def record_cost(input_tokens: int, output_tokens: int) -> float:
    cost = (input_tokens * PRICE_INPUT_PER_1K + output_tokens * PRICE_OUTPUT_PER_1K) / 1000
    key = _key()
    with r.pipeline() as pipe:
        pipe.incrbyfloat(key, cost).expire(key, 172800).execute()
    return cost
