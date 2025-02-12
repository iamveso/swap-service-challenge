import strawberry
from typing import List
from strawberry.types import Info
from strawberry.fastapi import BaseContext
from .path_finder import PathFinder
from .pool_loader import PoolLoader

@strawberry.type
class Token:
    symbol: str
    address: str | None = None

@strawberry.type
class Pool:
    token0: Token
    token1: Token
    price0: float
    price1: float
    fee: float

@strawberry.type
class SwapRoute:
    path: List[str]
    rate: float

# Define the context class inheriting from BaseContext
class Context(BaseContext):
    def __init__(self, pool_loader: PoolLoader, path_finder: PathFinder):
        super().__init__()
        self.pool_loader = pool_loader
        self.path_finder = path_finder

@strawberry.type
class Query:
    @strawberry.field
    async def available_tokens(self, info: Info[Context, None]) -> List[Token]:
        pools = await info.context.pool_loader.fetch_pools()
        tokens = set()
        for pool in pools:
            tokens.add(pool.token0.symbol)
            tokens.add(pool.token1.symbol)
        return [Token(symbol=t) for t in sorted(tokens)]

    @strawberry.field
    async def find_route(
        self, 
        info: Info[Context, None],
        from_token: str, 
        to_token: str
    ) -> SwapRoute:
        pools = await info.context.pool_loader.fetch_pools()
        info.context.path_finder.update_pools(pools)
        path, rate = info.context.path_finder.find_best_path(from_token, to_token)
        return SwapRoute(path=path, rate=rate)

schema = strawberry.Schema(query=Query)