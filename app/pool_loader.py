import httpx
import asyncio
from typing import List, Dict
from app.models import Pool, Token
from .utils import get_name_details
from .settings import logger, redis_client
import json

class PoolLoader:
    GECKOTERMINAL_API = "https://api.geckoterminal.com/api/v2/networks/eth/pools"
    POOL_CACHE_KEY = "pool_cache"
    async def fetch_pools(self, force: bool = True) -> List[Pool]:
        if not force:
            #get data from cache
            cached_pool = redis_client.get(self.POOL_CACHE_KEY)
            if cached_pool:
                cached_data = json.loads(cached_pool)
                cache = [Pool.model_validate(cached_data) for cached_data in cached_data]
                return cache
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(self.GECKOTERMINAL_API)
                    response.raise_for_status()
                    data = response.json()
                except Exception as e:
                    logger.error("failed to fetch pool attempt %d: %s", attempt + 1, e)
                    await asyncio.sleep(2 ** attempt)
                    if attempt >=2 :
                        return []
            
            pools: List[Pool] = []
            for pool_data in data.get("data", []):
                attrs = pool_data.get("attributes", {})
                baserels = pool_data["relationships"]["base_token"]["data"]
                quoterels = pool_data["relationships"]["quote_token"]["data"]
                tokenname1, tokenname2, fee = get_name_details(attrs["name"])
                # Create tokens
                token0 = Token(
                    symbol=tokenname1,
                    address=baserels["id"]
                )
                token1 = Token(
                    symbol=tokenname2,
                    address=quoterels["id"]
                )
                
                # Get prices and fee
                try:
                    price0 = float(attrs.get("base_token_price_quote_token", 0))
                    price1 = float(attrs.get("quote_token_price_base_token", 0))
                    
                    if price0 <= 0 or price1 <= 0 or fee <= 0:
                        continue
                    
                    pools.append(Pool(
                        token0=token0,
                        token1=token1,
                        price0=price0,
                        price1=price1,
                        fee=fee
                    ))
                except (ValueError, TypeError):
                    continue
            redis_client.flushdb()
            pools_json = json.dumps([pool.model_dump() for pool in pools])
            redis_client.set(self.POOL_CACHE_KEY, pools_json)
            return pools