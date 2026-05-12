from abc import ABC, abstractmethod
from typing import List
from src.domain.models import Stock, Recommendation

class IStockProvider(ABC):
    @abstractmethod
    def fetch_all_stocks(self) -> List[Stock]:
        pass

class INotifier(ABC):
    @abstractmethod
    def send_recommendations(self, recommendations: List[Recommendation]):
        pass

class IStorage(ABC):
    @abstractmethod
    def save_results(self, date_str: str, all_stocks: List[Stock], recommendations: List[Recommendation]):
        pass
    
    @abstractmethod
    def load_results(self, date_str: str) -> List[Recommendation]:
        pass
