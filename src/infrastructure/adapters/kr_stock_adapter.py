import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List
from src.domain.models import Stock, FinancialMetrics, MarketType
from src.domain.interfaces import IStockProvider
import time

class NaverAdapter(IStockProvider):
    def fetch_all_stocks(self) -> List[Stock]:
        stocks_list = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        try:
            all_tickers = []
            for sosok in [0, 1]:
                url = f"https://finance.naver.com/sise/sise_market_sum.nhn?sosok={sosok}"
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content.decode('euc-kr', errors='replace'), 'html.parser')
                table = soup.find('table', {'class': 'type_2'})
                if not table: continue
                
                rows = table.find_all('tr')
                market_tickers = []
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 2: continue
                    a_tag = cols[1].find('a', href=True)
                    if a_tag:
                        ticker = a_tag['href'].split('=')[-1]
                        name = a_tag.text
                        price = cols[2].text.replace(',', '')
                        market_tickers.append((ticker, name, float(price)))
                    if len(market_tickers) >= 100: break
                all_tickers.extend(market_tickers)
            
            print(f"Enriching {len(all_tickers)} KR stocks...")
            for ticker, name, price in all_tickers:
                try:
                    time.sleep(0.1)
                    item_url = f"https://finance.naver.com/item/main.nhn?code={ticker}"
                    item_res = requests.get(item_url, headers=headers)
                    # Use utf-8 for individual item page
                    item_soup = BeautifulSoup(item_res.content.decode('utf-8', errors='replace'), 'html.parser')
                    
                    invest_info = item_soup.find('div', {'class': 'aside_invest_info'})
                    per, pbr, div, roe, debt = None, None, None, None, None
                    sector = None
                    
                    if invest_info:
                        per_em = invest_info.find('em', id='_per')
                        if per_em: per = self._to_float(per_em.text)
                        pbr_em = invest_info.find('em', id='_pbr')
                        if pbr_em: pbr = self._to_float(pbr_em.text)
                        
                        # Sector (Fix: Precise extraction from trade_compare section)
                        compare_div = item_soup.find('div', {'class': 'trade_compare'})
                        if compare_div:
                            sector_a = compare_div.find('a', href=lambda x: x and 'sise_group_detail.naver?type=upjong' in x)
                            if sector_a:
                                sector = sector_a.text.strip()

                    cop_analysis = item_soup.find('div', {'class': 'section_cop_analysis'})
                    if cop_analysis:
                        table = cop_analysis.find('table')
                        if table:
                            for tr in table.find_all('tr'):
                                text = tr.text
                                if 'ROE' in text:
                                    tds = tr.find_all('td')
                                    if len(tds) >= 3: roe = self._to_float(tds[2].text)
                                if '부채비율' in text:
                                    tds = tr.find_all('td')
                                    if len(tds) >= 3: debt = self._to_float(tds[2].text)

                    stocks_list.append(Stock(
                        ticker=ticker,
                        name=name,
                        market=MarketType.KRX,
                        price=price,
                        sector=sector,
                        metrics=FinancialMetrics(
                            per=per, pbr=pbr, roe=roe, debt_ratio=debt, dividend_yield=div
                        )
                    ))
                except Exception:
                    continue
                    
            return stocks_list
            
        except Exception as e:
            print(f"Error fetching KRX stocks from Naver: {e}")
            return []

    def _to_float(self, val) -> float:
        if val is None or str(val) in ['N/A', '-', 'nan', '', 'N/A배', 'N/A%']:
            return None
        try:
            val_str = str(val).replace(',', '').replace('%', '').replace('배', '').strip()
            return float(val_str)
        except (ValueError, TypeError):
            return None
