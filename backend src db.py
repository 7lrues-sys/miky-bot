"""
File-level: Database helpers for Mikky backend.
Provides async connection pooling and helper functions.
"""

from typing import Optional, Any, Dict
import os
import asyncpg
import asyncio

DATABASE_URL = os.getenv("DATABASE_URL")

_pool: Optional[asyncpg.pool.Pool] = None

async def init_db_pool():
    """
    Initialize the asyncpg connection pool.
    Call this at application startup.
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)

async def close_db_pool():
    """
    Close the pool at shutdown.
    """
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

async def fetchrow(query: str, *args) -> Optional[asyncpg.Record]:
    """
    Execute a query and return a single row.
    """
    async with _pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def fetch(query: str, *args) -> list:
    """
    Execute a query and return all rows.
    """
    async with _pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def execute(query: str, *args) -> str:
    """
    Execute a statement (INSERT/UPDATE/DELETE).
    """
    async with _pool.acquire() as conn:
        return await conn.execute(query, *args)

async def fetchval(query: str, *args) -> Any:
    """
    Execute a query and return a single value.
    """
    async with _pool.acquire() as conn:
        return await conn.fetchval(query, *args)
