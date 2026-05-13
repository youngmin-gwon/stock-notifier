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
        
        # Calculate market-wide stats as a fallback
        market_stats = self._calculate_stats(stocks)
        # Calculate sector-specific stats
        sector_stats = self._calculate_sector_stats(stocks)
        
        for stock in stocks:
            # Use sector stats if available and has enough samples, otherwise fallback to market stats
            stats = sector_stats.get(stock.sector, market_stats)
            if stats.get("count", 0) < 3:
                stats = market_stats

            # 1. Value Track
            value_rec = self._assess_value(stock, stats)
            if value_rec: recommendations.append(value_rec)
            
            # 2. Quality Track
            quality_rec = self._assess_quality(stock, stats)
            if quality_rec: recommendations.append(quality_rec)
                
        return recommendations

    def _calculate_stats(self, stocks: List[Stock]) -> Dict[str, float]:
        pers = [s.metrics.per for s in stocks if s.metrics.per and s.metrics.per > 0]
        pbrs = [s.metrics.pbr for s in stocks if s.metrics.pbr and s.metrics.pbr > 0]
        roes = [s.metrics.roe for s in stocks if s.metrics.roe]
        debts = [s.metrics.debt_ratio for s in stocks if s.metrics.debt_ratio]
        
        return {
            "avg_per": statistics.mean(pers) if pers else self.max_per,
            "avg_pbr": statistics.mean(pbrs) if pbrs else self.max_pbr,
            "avg_roe": statistics.mean(roes) if roes else 0,
            "avg_debt": statistics.mean(debts) if debts else 0,
            "count": len(stocks)
        }

    def _calculate_sector_stats(self, stocks: List[Stock]) -> Dict[str, Dict[str, float]]:
        sector_map = {}
        sectors = set(s.sector for s in stocks if s.sector)
        
        for sector in sectors:
            sector_stocks = [s for s in stocks if s.sector == sector]
            sector_map[sector] = self._calculate_stats(sector_stocks)
            sector_map[sector]["count"] = len(sector_stocks)
            
        return sector_map

    def _assess_value(self, stock: Stock, stats: Dict) -> Optional[Recommendation]:
        m = stock.metrics
        if not m.per or not m.pbr: return None
        if m.per > self.max_per or m.pbr > self.max_pbr: return None
        
        avg_per = stats.get("avg_per", self.max_per)
        avg_pbr = stats.get("avg_pbr", self.max_pbr)
        
        # If the stock is significantly cheaper than the benchmark (sector or market)
        if m.per < avg_per * 0.85 and m.pbr < avg_pbr * 0.85:
            score = (avg_per - m.per) + (avg_pbr - m.pbr) * 10
            bench_type = "Sector" if stats.get("count", 0) < 500 else "Market" # Simplified check
            return Recommendation(
                stock=stock,
                category="Value",
                reason=f"Deep Value relative to {bench_type}",
                score=score,
                sector_stats=stats
            )
        return None

    def _assess_quality(self, stock: Stock, stats: Dict) -> Optional[Recommendation]:
        m = stock.metrics
        if not m.roe or not m.debt_ratio: return None
        if m.roe < self.min_roe or m.debt_ratio > self.max_debt_ratio: return None
        
        avg_roe = stats.get("avg_roe", 0)
        
        # Quality: ROE must be better than the benchmark
        if m.roe > avg_roe:
            score = m.roe - (m.debt_ratio / 10)
            return Recommendation(
                stock=stock,
                category="Quality",
                reason=f"High Quality relative to Benchmark",
                score=score,
                sector_stats=stats
            )
        return None
