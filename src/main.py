import os
import random
import FinanceDataReader as fdr
from dotenv import load_dotenv
from src.infrastructure.adapters.kr_stock_adapter import NaverAdapter
from src.infrastructure.adapters.yfinance_adapter import YFinanceAdapter
from src.infrastructure.notifiers import DiscordNotifier
from src.infrastructure.storage import FileStorage
from src.domain.services import DualAnalysisStrategy
from src.application.services import StockAnalysisService

def main():
    # Load environment variables
    load_dotenv()
    
    # Only the Discord URL is kept as an environment variable
    discord_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    # Strategy thresholds
    MAX_PER = 15.0
    MAX_PBR = 1.5
    MIN_ROE = 10.0
    MAX_DEBT = 150.0

    # Initialize components
    print("Fetching US ticker list (Diverse Selection)...")
    try:
        sp500 = fdr.StockListing('S&P500')
        # Instead of head(100), shuffle to get a more diverse sample of US stocks
        all_us_tickers = sp500['Symbol'].tolist()
        random.seed(42) # Deterministic for now but diverse
        us_tickers = random.sample(all_us_tickers, min(len(all_us_tickers), 100))
    except Exception as e:
        print(f"Error fetching S&P500 list: {e}")
        us_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B"]
    
    providers = [
        NaverAdapter(),
        YFinanceAdapter(tickers=us_tickers)
    ]
    
    strategy = DualAnalysisStrategy(
        max_per=MAX_PER,
        max_pbr=MAX_PBR,
        min_roe=MIN_ROE,
        max_debt_ratio=MAX_DEBT
    )
    
    notifier = DiscordNotifier(webhook_url=discord_url)
    storage = FileStorage()
    
    app_service = StockAnalysisService(
        providers=providers,
        strategy=strategy,
        notifier=notifier,
        storage=storage
    )
    
    app_service.run_daily_scan()

if __name__ == "__main__":
    main()
