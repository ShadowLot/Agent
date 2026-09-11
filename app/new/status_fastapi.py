import os
import time
import json
import asyncio
from typing import List, Dict, Any
import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Config: set HEALTH_TARGETS as JSON in env, e.g.
# HEALTH_TARGETS='[{"name":"users","url":"https://api.example.com/users/health","required":true},{"name":"search","url":"https://search.example.com/ping","required":false}]'
TARGETS_ENV = os.getenv("HEALTH_TARGETS", "[]")
DEFAULT_TTL = int(os.getenv("HEALTH_TTL_SECONDS", "5"))

try:
    TARGETS: List[Dict[str, Any]] = json.loads(TARGETS_ENV)
except Exception:
    TARGETS = []

router = APIRouter()

# simple in-memory cache
_cache = {"ts": 0.0, "payload": None}
_cache_lock = asyncio.Lock()

async def probe_one(client: httpx.AsyncClient, target: Dict[str, Any]) -> Dict[str, Any]:
    name = target.get("name") or target.get("url")
    url = target["url"]
    timeout = target.get("timeout", 2.0)
    expected = target.get("expected_statuses", [200])
    headers = target.get("headers")
    start = time.monotonic()
    try:
        r = await client.get(url, headers=headers, timeout=timeout)
        latency_ms = (time.monotonic() - start) * 1000
        ok = r.status_code in expected
        return {
            "name": name,
            "url": url,
            "ok": ok,
            "http_status": r.status_code,
            "latency_ms": round(latency_ms, 1),
            "error": None,
        }
    except Exception as e:
        latency_ms = (time.monotonic() - start) * 1000
        return {
            "name": name,
            "url": url,
            "ok": False,
            "http_status": None,
            "latency_ms": round(latency_ms, 1),
            "error": str(e),
        }

async def run_probes(targets: List[Dict[str, Any]]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        tasks = [probe_one(client, t) for t in targets]
        results = await asyncio.gather(*tasks, return_exceptions=False)

    overall_ok = True
    for t, res in zip(targets, results):
        required = t.get("required", True)
        if required and not res.get("ok", False):
            overall_ok = False
            break

    overall = "ok" if overall_ok else "degraded"
    payload = {
        "status": overall,
        "services": results,
        "timestamp": int(time.time()),
    }
    return payload

async def get_status(ttl: int = DEFAULT_TTL, force_refresh: bool = False):
    now = time.time()
    async with _cache_lock:
        if not force_refresh and _cache["payload"] and now - _cache["ts"] < ttl:
            return _cache["payload"]
        payload = await run_probes(TARGETS)
        _cache["payload"] = payload
        _cache["ts"] = now
        return payload

@router.get("/status")
async def status():
    payload = await get_status()
    any_down = any((s["ok"] is False and next((t for t in TARGETS if (t.get("name") or t.get("url")) == s["name"]), {}).get("required", True)) for s in payload["services"])
    return JSONResponse(content=payload, status_code=(200 if not any_down else 503))
