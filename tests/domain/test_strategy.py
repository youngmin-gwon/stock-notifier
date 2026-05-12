import pytest
from src.domain.models import FinancialMetrics, MarketType, Stock
from src.domain.services import UndervaluedStrategy

def test_undervalued_strategy_should_satisfy_low_metrics():
    # Arrange: Create metrics that are clearly undervalued
    metrics = FinancialMetrics(per=5.0, pbr=0.5, psr=0.2)
    strategy = UndervaluedStrategy(max_per=10.0, max_pbr=1.0, max_psr=1.0)

    # Act: Check if the strategy is satisfied
    result = strategy.is_satisfied_by(metrics)

    # Assert: Should be True
    assert result is True

def test_undervalued_strategy_should_reject_high_per():
    # Arrange: Create metrics with high PER
    metrics = FinancialMetrics(per=15.0, pbr=0.5, psr=0.2)
    strategy = UndervaluedStrategy(max_per=10.0)

    # Act: Check if the strategy is satisfied
    result = strategy.is_satisfied_by(metrics)

    # Assert: Should be False
    assert result is False

def test_undervalued_strategy_should_reject_negative_metrics():
    # Arrange: Negative PER is usually a sign of loss, not "undervalued" in this context
    metrics = FinancialMetrics(per=-5.0, pbr=0.5)
    strategy = UndervaluedStrategy()

    # Act
    result = strategy.is_satisfied_by(metrics)

    # Assert
    assert result is False

def test_undervalued_strategy_assessment_returns_recommendation():
    # Arrange
    stock = Stock(
        ticker="005930",
        name="Samsung Electronics",
        market=MarketType.KRX,
        price=70000,
        metrics=FinancialMetrics(per=8.0, pbr=0.9)
    )
    strategy = UndervaluedStrategy()

    # Act
    recommendation = strategy.assess(stock)

    # Assert
    assert recommendation is not None
    assert "Low valuation" in recommendation.reason
    assert recommendation.stock.ticker == "005930"
