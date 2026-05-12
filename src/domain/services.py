from typing import List, Optional, Dict
from src.domain.models import Stock, Recommendation, FinancialMetrics
import statistics

class DualAnalysisStrategy:
    def __init__(
        self, 
        max_per: float = 15.0, 
        max_pbr: float = 1.5,
        min_roe: float = 10.0,
        max_debt_ratio: float = 150.0
    ):
        self.max_per = max_per
        self.max_pbr = max_pbr
        self.min_roe = min_roe
        self.max_debt_ratio = max_debt_ratio

    def analyze_all(self, stocks: List[Stock]) -> List[Recommendation]:
        recommendations = []
        sector_stats = self._calculate_sector_stats(stocks)
        
        for stock in stocks:
            value_rec = self._assess_value(stock, sector_stats)
            if value_rec: recommendations.append(value_rec)
            
            quality_rec = self._assess_quality(stock, sector_stats)
            if quality_rec: recommendations.append(quality_rec)
                
        return recommendations

    def _calculate_sector_stats(self, stocks: List[Stock]) -> Dict[str, Dict[str, float]]:
        stats = {}
        sectors = set(s.sector for s in stocks if s.sector)
        
        for sector in sectors:
            sector_stocks = [s for s in stocks if s.sector == sector]
            pers = [s.metrics.per for s in sector_stocks if s.metrics.per and s.metrics.per > 0]
            pbrs = [s.metrics.pbr for s in sector_stocks if s.metrics.pbr and s.metrics.pbr > 0]
            roes = [s.metrics.roe for s in sector_stocks if s.metrics.roe]
            debts = [s.metrics.debt_ratio for s in sector_stocks if s.metrics.debt_ratio]
            
            stats[sector] = {
                "avg_per": statistics.mean(pers) if pers else 0,
                "avg_pbr": statistics.mean(pbrs) if pbrs else 0,
                "avg_roe": statistics.mean(roes) if roes else 0,
                "avg_debt": statistics.mean(debts) if debts else 0
            }
        return stats

    def _assess_value(self, stock: Stock, sector_stats: Dict) -> Optional[Recommendation]:
        m = stock.metrics
        if not m.per or not m.pbr: return None
        if m.per > self.max_per or m.pbr > self.max_pbr: return None
        
        stats = sector_stats.get(stock.sector, {})
        avg_per = stats.get("avg_per", self.max_per)
        avg_pbr = stats.get("avg_pbr", self.max_pbr)
        
        if m.per < avg_per * 0.8 and m.pbr < avg_pbr * 0.8:
            score = (avg_per - m.per) + (avg_pbr - m.pbr) * 10
            return Recommendation(
                stock=stock,
                category="Value",
                reason=f"Deep Value relative to {stock.sector}",
                score=score,
                sector_stats=stats
            )
        return None

    def _assess_quality(self, stock: Stock, sector_stats: Dict) -> Optional[Recommendation]:
        m = stock.metrics
        if not m.roe or not m.debt_ratio: return None
        if m.roe < self.min_roe or m.debt_ratio > self.max_debt_ratio: return None
        
        stats = sector_stats.get(stock.sector, {})
        avg_roe = stats.get("avg_roe", 0)
        
        # High Quality: ROE must be better than sector average
        if m.roe > avg_roe:
            score = m.roe - (m.debt_ratio / 10)
            return Recommendation(
                stock=stock,
                category="Quality",
                reason=f"High Quality relative to {stock.sector}",
                score=score,
                sector_stats=stats
            )
        return None
