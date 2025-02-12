from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    symbol: str
    address: Optional[str] | None = None
    
    def __str__(self):
        return self.symbol

class Pool(BaseModel):
    token0: Token
    token1: Token
    price0: float  # Price of token0 in terms of token1
    price1: float  # Price of token1 in terms of token0
    fee: float     # Fee as a decimal (0.003 = 0.3%)
    
    def __str__(self):
        return f"{self.token0}/{self.token1}"