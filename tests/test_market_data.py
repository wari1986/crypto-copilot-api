from datetime import datetime
from decimal import Decimal

import pytest

from app.services.market_data import sentiment
from app.services.market_data.ccxt_adapter import CcxtAdapter


class DummyExchange:
    async def fetch_order_book(self, symbol: str, limit: int = 50):
        return {
            "bids": [[1, 2]],
            "asks": [[1.1, 3]],
            "timestamp": 1_700_000_000_000,
        }

    async def fetch_trades(self, symbol: str, since=None, limit=200):
        return [
            {"timestamp": 1_700_000_000_000, "price": 10, "amount": 0.5, "side": "buy"},
        ]


@pytest.mark.asyncio
async def test_fetch_l2_orderbook(monkeypatch):
    adapter = CcxtAdapter()
    adapter._client = DummyExchange()
    ob = await adapter.fetch_l2_orderbook("BTC/USDT", limit=1)
    assert ob["bids"][0]["price"] == Decimal("1")
    assert ob["asks"][0]["volume"] == Decimal("3")


@pytest.mark.asyncio
async def test_fetch_sentiment(monkeypatch):
    class DummyResp:
        def json(self):
            return {
                "data": [
                    {
                        "value": "50",
                        "value_classification": "Neutral",
                        "timestamp": "1710000000",
                    },
                ],
            }

        def raise_for_status(self):
            pass

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, _timeout=10.0):
            return DummyResp()

    monkeypatch.setattr(sentiment.httpx, "AsyncClient", lambda: DummyClient())
    data = await sentiment.fetch_fear_greed_index()
    assert data["value"] == 50
    assert data["classification"] == "Neutral"
    assert isinstance(data["ts"], datetime)
