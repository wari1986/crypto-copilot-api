from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_market_data"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extend instruments with spot fields
    op.add_column("instruments", sa.Column("venue", sa.String(length=20), nullable=True))
    op.add_column("instruments", sa.Column("type", sa.String(length=10), nullable=True))
    op.add_column("instruments", sa.Column("settlement", sa.String(length=20), nullable=True))
    op.add_column("instruments", sa.Column("tick_size_num", sa.Numeric(38, 18), nullable=True))
    op.add_column("instruments", sa.Column("lot_size_num", sa.Numeric(38, 18), nullable=True))
    op.add_column("instruments", sa.Column("min_notional_num", sa.Numeric(38, 18), nullable=True))
    op.add_column("instruments", sa.Column("contract_size", sa.Numeric(38, 18), nullable=True))
    op.add_column("instruments", sa.Column("price_scale", sa.Integer(), nullable=True))
    op.add_column("instruments", sa.Column("qty_scale", sa.Integer(), nullable=True))
    op.add_column("instruments", sa.Column("maker_fee_bps", sa.Numeric(38, 18), nullable=True))
    op.add_column("instruments", sa.Column("taker_fee_bps", sa.Numeric(38, 18), nullable=True))
    op.add_column("instruments", sa.Column("max_leverage", sa.Numeric(38, 18), nullable=True))
    op.create_unique_constraint("uq_instrument_venue_symbol", "instruments", ["venue", "symbol"])

    # Enums will be created implicitly by SQLAlchemy when creating tables below

    # OHLCV 1m
    op.create_table(
        "ohlcv_1m",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "instrument_id",
            sa.Integer(),
            sa.ForeignKey("instruments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(38, 18), nullable=False),
        sa.Column("high", sa.Numeric(38, 18), nullable=False),
        sa.Column("low", sa.Numeric(38, 18), nullable=False),
        sa.Column("close", sa.Numeric(38, 18), nullable=False),
        sa.Column("volume_base", sa.Numeric(38, 18), nullable=False),
        sa.Column("turnover_quote", sa.Numeric(38, 18), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
        sa.UniqueConstraint("instrument_id", "ts", name="uq_ohlcv1m_unique"),
    )
    op.create_index("ix_ohlcv1m_ts", "ohlcv_1m", ["ts"])

    # Ticker RT
    op.create_table(
        "ticker_rt",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "instrument_id",
            sa.Integer(),
            sa.ForeignKey("instruments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last", sa.Numeric(38, 18), nullable=False),
        sa.Column("bid", sa.Numeric(38, 18), nullable=False),
        sa.Column("ask", sa.Numeric(38, 18), nullable=False),
        sa.Column("mid", sa.Numeric(38, 18), nullable=False),
        sa.Column("spread_bps", sa.Numeric(38, 18), nullable=False),
        sa.Column("day_vol_quote", sa.Numeric(38, 18), nullable=True),
        sa.Column("mark", sa.Numeric(38, 18), nullable=True),
        sa.Column("index", sa.Numeric(38, 18), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
    )
    op.create_index("ix_tickerrt_ts", "ticker_rt", ["ts"])

    # Orderbook L2
    op.create_table(
        "orderbook_l2",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "instrument_id",
            sa.Integer(),
            sa.ForeignKey("instruments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("side", sa.Enum("bid", "ask", name="ob_side_enum"), nullable=False),
        sa.Column("px", sa.Numeric(38, 18), nullable=False),
        sa.Column("qty", sa.Numeric(38, 18), nullable=False),
        sa.Column("snapshot_id", sa.String(length=36), nullable=True),
        sa.Column("update_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
    )
    op.create_index("ix_ob_l2_instr_ts_side", "orderbook_l2", ["instrument_id", "ts", "side"])

    # Trades RT
    op.create_table(
        "trade_rt",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "instrument_id",
            sa.Integer(),
            sa.ForeignKey("instruments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("px", sa.Numeric(38, 18), nullable=False),
        sa.Column("qty", sa.Numeric(38, 18), nullable=False),
        sa.Column("side", sa.Enum("buy", "sell", name="trade_side_enum"), nullable=False),
        sa.Column("trade_id", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False,
        ),
        sa.UniqueConstraint("instrument_id", "trade_id", name="uq_trade_rt_unique"),
    )
    op.create_index("ix_tradert_ts", "trade_rt", ["ts"])


def downgrade() -> None:
    op.drop_index("ix_tradert_ts", table_name="trade_rt")
    op.drop_table("trade_rt")
    op.drop_index("ix_ob_l2_instr_ts_side", table_name="orderbook_l2")
    op.drop_table("orderbook_l2")
    op.drop_index("ix_tickerrt_ts", table_name="ticker_rt")
    op.drop_table("ticker_rt")
    op.drop_index("ix_ohlcv1m_ts", table_name="ohlcv_1m")
    op.drop_table("ohlcv_1m")
    op.execute("DROP TYPE IF EXISTS trade_side_enum")
    op.execute("DROP TYPE IF EXISTS ob_side_enum")
    op.drop_constraint("uq_instrument_venue_symbol", "instruments", type_="unique")
    for col in [
        "venue",
        "type",
        "settlement",
        "tick_size_num",
        "lot_size_num",
        "min_notional_num",
        "contract_size",
        "price_scale",
        "qty_scale",
        "maker_fee_bps",
        "taker_fee_bps",
        "max_leverage",
    ]:
        op.drop_column("instruments", col)
