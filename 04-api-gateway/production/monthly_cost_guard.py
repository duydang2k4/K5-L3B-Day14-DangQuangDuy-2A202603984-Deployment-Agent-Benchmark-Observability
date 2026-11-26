"""Atomic monthly budget reservation in Redis (UTC)."""
import hashlib
import math
from datetime import datetime, timezone

import redis

_RESERVE = """
local current = tonumber(redis.call('GET', KEYS[1]) or '0')
local estimate = tonumber(ARGV[1])
if current + estimate > tonumber(ARGV[2]) then return 0 end
redis.call('INCRBYFLOAT', KEYS[1], estimate)
redis.call('EXPIRE', KEYS[1], ARGV[3])
return 1
"""

def check_budget(user_id: str, estimated_cost: float, client: redis.Redis) -> bool:
    """Reserve an estimated USD cost if the user's monthly budget allows it."""
    if not user_id or not math.isfinite(estimated_cost) or estimated_cost < 0:
        raise ValueError('A user and a finite non-negative cost are required')
    month = datetime.now(timezone.utc).strftime('%Y-%m')
    user_hash = hashlib.sha256(user_id.encode()).hexdigest()
    return bool(client.eval(_RESERVE, 1, f'budget:{user_hash}:{month}', estimated_cost, 10, 32 * 86400))
