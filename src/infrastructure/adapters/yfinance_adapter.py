import yfinance as yf
from typing import List
from src.domain.models import Stock, FinancialMetrics, MarketType
from src.domain.interfaces import IStockProvider
import time
import random

class YFinanceAdapter(IStockProvider):
    def __init__(self, tickers: List[str]):
        self.tickers = tickers

    def fetch_all_stocks(self) -> List[Stock]:
        stocks_list = []
        print(f"Fetching {len(self.tickers)} US stocks from yfinance with quality metrics...")
        
        for ticker in self.tickers:
            try:
                time.sleep(0.3)
                yt = yf.Ticker(ticker)
                info = yt.info
                
                per = info.get('trailingPE') or info.get('forwardPE')
                pbr = info.get('priceToBook')
                
                # ROE and Debt Ratio
                roe = info.get('returnOnEquity')
                if roe: roe *= 100 # Convert to percentage
                
                debt_ratio = info.get('debtToEquity') # Usually already in percentage or ratio
                
                metrics = FinancialMetrics(
                    per=per,
                    pbr=pbr,
                    roe=roe,
                    debt_ratio=debt_ratio,
                    dividend_yield=info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None
                )
                
                stocks_list.append(Stock(
                    ticker=ticker,
                    name=info.get('shortName', ticker),
                    market=MarketType.NASDAQ if ".T" not in ticker else MarketType.NYSE,
                    price=info.get('currentPrice') or info.get('regularMarketPrice') or 0.0,
                    sector=info.get('sector'),
                    metrics=metrics
                ))
            except Exception as e:
                if "429" in str(e):
                    time.sleep(5)
                else:
                    print(f"Error fetching US stock {ticker}: {e}")
                
        return stocks_list
