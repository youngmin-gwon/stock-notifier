import json
import os
from typing import List
from src.domain.models import Recommendation, Stock, FinancialMetrics, MarketType
from src.domain.interfaces import IStorage

class FileStorage(IStorage):
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def save_results(self, date_str: str, all_stocks: List[Stock], recommendations: List[Recommendation]):
        file_path = os.path.join(self.base_dir, f"{date_str}.json")
        
        rec_data = []
        for rec in recommendations:
            rec_data.append(self._serialize_stock(rec.stock, extra={
                "reason": rec.reason, 
                "score": rec.score,
                "category": rec.category
            }))
            
        all_data = []
        for stock in all_stocks:
            all_data.append(self._serialize_stock(stock))
            
        full_data = {
            "date": date_str,
            "summary": {
                "total_scanned": len(all_stocks),
                "total_recommended": len(recommendations)
            },
            "recommendations": rec_data,
            "all_scanned_stocks": all_data
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(full_data, f, ensure_ascii=False, indent=4)

    def _serialize_stock(self, stock: Stock, extra: dict = None) -> dict:
        data = {
            "ticker": stock.ticker,
            "name": stock.name,
            "market": stock.market.value,
            "price": stock.price,
            "sector": stock.sector,
            "metrics": {
                "per": stock.metrics.per,
                "pbr": stock.metrics.pbr,
                "psr": stock.metrics.psr,
                "roe": stock.metrics.roe,
                "debt_ratio": stock.metrics.debt_ratio,
                "div": stock.metrics.dividend_yield
            }
        }
        if extra:
            data.update(extra)
        return data

    def load_results(self, date_str: str) -> List[Recommendation]:
        # Minimal implementation for now
        return []
