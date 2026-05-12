from dataclasses import dataclass, field
from typing import Optional, Dict
from enum import Enum

class MarketType(Enum):
    KRX = "KRX"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"

@dataclass
class FinancialMetrics:
    per: Optional[float] = None
    pbr: Optional[float] = None
    psr: Optional[float] = None
    roe: Optional[float] = None
    debt_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

@dataclass
class Stock:
    ticker: str
    name: str
    market: MarketType
    price: float
    metrics: FinancialMetrics
    sector: Optional[str] = None

@dataclass
class Recommendation:
    stock: Stock
    reason: str
    score: float
    category: str = "Value"
    sector_stats: Dict[str, float] = field(default_factory=dict) # New: Store comparison benchmarks
