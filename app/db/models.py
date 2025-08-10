from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Exchange(str, enum.Enum):
    BYBIT = "BYBIT"


class CandleInterval(str, enum.Enum):
    m1 = "1m"
    m5 = "5m"
    h1 = "1h"


class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, enum.Enum):
    LIMIT = "limit"
    MARKET = "market"
    POST_ONLY = "post_only"
    IOC = "ioc"


class OrderStatus(str, enum.Enum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"


class PositionSide(str, enum.Enum):
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


class Instrument(TimestampMixin, Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    base_asset: Mapped[str] = mapped_column(String(20), nullable=False)
    quote_asset: Mapped[str] = mapped_column(String(20), nullable=False)
    exchange: Mapped[Exchange] = mapped_column(
        Enum(Exchange, name="exchange_enum", native_enum=False), nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="TRADING")
    tick_size: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    step_size: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_notional: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Spot market data extensions (nullable for compatibility)
    venue: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="bybit")
    type: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="spot")
    settlement: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tick_size_num: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    lot_size_num: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    min_notional_num: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    contract_size: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    price_scale: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    qty_scale: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    maker_fee_bps: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    taker_fee_bps: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    max_leverage: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)

    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="uq_instrument_symbol_exchange"),
        UniqueConstraint("venue", "symbol", name="uq_instrument_venue_symbol"),
        Index("ix_instruments_symbol", "symbol"),
    )


class Candle(TimestampMixin, Base):
    __tablename__ = "candles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False,
    )


# Spot-only market data tables (v1)


class OHLCV1m(TimestampMixin, Base):
    __tablename__ = "ohlcv_1m"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False,
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    volume_base: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    turnover_quote: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)

    __table_args__ = (
        UniqueConstraint("instrument_id", "ts", name="uq_ohlcv1m_unique"),
        Index("ix_ohlcv1m_ts", "ts"),
    )


class TickerRT(TimestampMixin, Base):
    __tablename__ = "ticker_rt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False,
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    bid: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    ask: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    mid: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    spread_bps: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    day_vol_quote: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    mark: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)
    index: Mapped[Optional[Decimal]] = mapped_column(Numeric(38, 18), nullable=True)

    __table_args__ = (Index("ix_tickerrt_ts", "ts"),)


class OBSide(str, enum.Enum):
    bid = "bid"
    ask = "ask"


class OrderBookL2(TimestampMixin, Base):
    __tablename__ = "orderbook_l2"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False,
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    side: Mapped[OBSide] = mapped_column(
        Enum(OBSide, name="ob_side_enum", native_enum=False), nullable=False,
    )
    px: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    qty: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    snapshot_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    update_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (Index("ix_ob_l2_instr_ts_side", "instrument_id", "ts", "side"),)


class TradeSide(str, enum.Enum):
    buy = "buy"
    sell = "sell"


class TradeRT(TimestampMixin, Base):
    __tablename__ = "trade_rt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False,
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    px: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    qty: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    side: Mapped[TradeSide] = mapped_column(
        Enum(TradeSide, name="trade_side_enum", native_enum=False), nullable=False,
    )
    trade_id: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("instrument_id", "trade_id", name="uq_trade_rt_unique"),
        Index("ix_tradert_ts", "ts"),
    )
    interval: Mapped[CandleInterval] = mapped_column(
        Enum(CandleInterval, name="candle_interval_enum", native_enum=False), nullable=False,
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("instrument_id", "interval", "ts", name="uq_candle_unique"),
        Index("ix_candles_ts", "ts"),
    )


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_order_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False,
    )
    side: Mapped[OrderSide] = mapped_column(
        Enum(OrderSide, name="order_side_enum", native_enum=False), nullable=False,
    )
    type: Mapped[OrderType] = mapped_column(
        Enum(OrderType, name="order_type_enum", native_enum=False), nullable=False,
    )
    qty: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum", native_enum=False),
        nullable=False,
        default=OrderStatus.NEW,
    )
    exchange_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    meta: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), nullable=True,
    )

    fills: Mapped[list[Fill]] = relationship(
        "Fill", back_populates="order", cascade="all, delete-orphan",
    )


class Fill(TimestampMixin, Base):
    __tablename__ = "fills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False,
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    qty: Mapped[float] = mapped_column(Float, nullable=False)
    fee: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fee_asset: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped[Order] = relationship("Order", back_populates="fills")


class Position(TimestampMixin, Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False,
    )
    side: Mapped[PositionSide] = mapped_column(
        Enum(PositionSide, name="position_side_enum", native_enum=False), nullable=False,
    )
    qty: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unrealized_pnl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    realized_pnl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    __table_args__ = (Index("ix_positions_instrument_id", "instrument_id"),)


class Config(TimestampMixin, Base):
    __tablename__ = "configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), nullable=True,
    )


class ModelDecision(TimestampMixin, Base):
    __tablename__ = "model_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow,
    )
    request_id: Mapped[str] = mapped_column(String(36), nullable=False)
    input_context_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    decision_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), nullable=True,
    )
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    signoff_user: Mapped[str | None] = mapped_column(String(100), nullable=True)
    applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    applied_ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
