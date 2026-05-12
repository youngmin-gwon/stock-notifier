from typing import List
from datetime import datetime
from src.domain.interfaces import IStockProvider, INotifier, IStorage
from src.domain.services import DualAnalysisStrategy

class StockAnalysisService:
    def __init__(
        self, 
        providers: List[IStockProvider], 
        strategy: DualAnalysisStrategy,
        notifier: INotifier,
        storage: IStorage
    ):
        self.providers = providers
        self.strategy = strategy
        self.notifier = notifier
        self.storage = storage

    def run_daily_scan(self):
        print(f"Starting upgraded daily scan at {datetime.now()}")
        all_scanned_stocks = []
        
        for provider in self.providers:
            stocks = provider.fetch_all_stocks()
            print(f"Fetched {len(stocks)} stocks from {provider.__class__.__name__}")
            all_scanned_stocks.extend(stocks)
        
        # Analyze using Dual Strategy (Value & Quality)
        print("Analyzing stocks using Dual Strategy (Relative Value + Quality)...")
        all_recommendations = self.strategy.analyze_all(all_scanned_stocks)
        
        # Sort recommendations by score (descending)
        all_recommendations.sort(key=lambda x: x.score, reverse=True)
        
        # Save results (All stocks + Recommendations)
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.storage.save_results(date_str, all_scanned_stocks, all_recommendations)
        
        # Notify
        self.notifier.send_recommendations(all_recommendations)
        print(f"Daily scan completed. Found {len(all_recommendations)} recommendations across all tracks.")
