from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
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
        Enum(Exchange, name="exchange_enum", native_enum=False), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="TRADING")
    tick_size: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    step_size: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_notional: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="uq_instrument_symbol_exchange"),
        Index("ix_instruments_symbol", "symbol"),
    )


class Candle(TimestampMixin, Base):
    __tablename__ = "candles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="CASCADE"), nullable=False
    )
    interval: Mapped[CandleInterval] = mapped_column(
        Enum(CandleInterval, name="candle_interval_enum", native_enum=False), nullable=False
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
        ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    side: Mapped[OrderSide] = mapped_column(
        Enum(OrderSide, name="order_side_enum", native_enum=False), nullable=False
    )
    type: Mapped[OrderType] = mapped_column(
        Enum(OrderType, name="order_type_enum", native_enum=False), nullable=False
    )
    qty: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum", native_enum=False),
        nullable=False,
        default=OrderStatus.NEW,
    )
    exchange_order_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    meta: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), nullable=True
    )

    fills: Mapped[list["Fill"]] = relationship(
        "Fill", back_populates="order", cascade="all, delete-orphan"
    )


class Fill(TimestampMixin, Base):
    __tablename__ = "fills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    qty: Mapped[float] = mapped_column(Float, nullable=False)
    fee: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fee_asset: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="fills")


class Position(TimestampMixin, Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.id", ondelete="RESTRICT"), nullable=False
    )
    side: Mapped[PositionSide] = mapped_column(
        Enum(PositionSide, name="position_side_enum", native_enum=False), nullable=False
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
        JSONB().with_variant(JSON, "sqlite"), nullable=True
    )


class ModelDecision(TimestampMixin, Base):
    __tablename__ = "model_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    request_id: Mapped[str] = mapped_column(String(36), nullable=False)
    input_context_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    decision_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"), nullable=True
    )
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signoff_user: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    applied_ts: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
