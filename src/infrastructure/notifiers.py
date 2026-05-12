import requests
from typing import List
from src.domain.models import Recommendation, MarketType
from src.domain.interfaces import INotifier

class DiscordNotifier(INotifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_recommendations(self, recommendations: List[Recommendation]):
        if not recommendations:
            self._send_to_discord("오늘 스캔 결과, 추천할만한 종목이 없습니다.")
            return

        value_recs = [r for r in recommendations if r.category == "Value"]
        quality_recs = [r for r in recommendations if r.category == "Quality"]

        message = "🚀 **오늘의 스마트 주식 브리핑** 🚀\n"
        message += "*(모든 지표는 업종 평균과 비교되었습니다)*\n\n"
        
        if value_recs:
            message += "💰 **[Deep Value] 가성비 킹**\n"
            for rec in value_recs[:5]:
                message += self._format_rec(rec)
            message += "\n"

        if quality_recs:
            message += "🏆 **[High Quality] 슈퍼 우량주**\n"
            for rec in quality_recs[:5]:
                message += self._format_rec(rec)
                
        if not self.webhook_url:
            print("Warning: Discord Webhook URL not set. Printing to console instead.")
            print(message)
            return

        self._send_to_discord(message)

    def _format_rec(self, rec: Recommendation) -> str:
        s = rec.stock
        m = s.metrics
        stats = rec.sector_stats
        market_icon = "🇰🇷" if s.market == MarketType.KRX else "🇺🇸"
        
        # Comparison logic for UX
        def compare(val, avg, better_if_lower=True):
            if not val or not avg: return ""
            diff = ((val - avg) / avg) * 100
            if better_if_lower:
                icon = "✅" if val < avg else "⚠️"
                status = f"{abs(diff):.0f}% 저렴" if val < avg else f"{abs(diff):.0f}% 고평가"
            else:
                icon = "🔥" if val > avg else "📉"
                status = f"{abs(diff):.0f}% 우수" if val > avg else f"{abs(diff):.0f}% 미달"
            return f" {icon} ({status})"

        per_ctx = compare(m.per, stats.get("avg_per"))
        pbr_ctx = compare(m.pbr, stats.get("avg_pbr"))
        roe_ctx = compare(m.roe, stats.get("avg_roe"), better_if_lower=False)
        debt_ctx = compare(m.debt_ratio, stats.get("avg_debt"))

        res = f"- {market_icon} **{s.name}** ({s.ticker}) | {s.sector}\n"
        if m.per: res += f"  • PER: {m.per:.1f}{per_ctx}\n"
        if m.pbr: res += f"  • PBR: {m.pbr:.1f}{pbr_ctx}\n"
        if m.roe: res += f"  • ROE: {m.roe:.1f}%{roe_ctx}\n"
        if m.debt_ratio: res += f"  • 부채: {m.debt_ratio:.1f}%{debt_ctx}\n"
        return res

    def _send_to_discord(self, content: str):
        try:
            if len(content) > 2000:
                content = content[:1990] + "..."
            payload = {"content": content}
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending to Discord: {e}")
