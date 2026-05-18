# =========================================================
# PART 1
# FOR STOCKS - CAPSTONE INSTITUTIONAL ENGINE
# IMPORTS + LOGIN + TELEGRAM + CSV + FILTERS
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import ta
import os
import time

from kiteconnect import KiteConnect

from datetime import (
    datetime,
    timedelta
)

# =========================================================
# STREAMLIT SETTINGS
# =========================================================

st.set_page_config(
    page_title="FOR STOCKS ENGINE",
    layout="wide"
)

st.title(
    "FOR STOCKS - CAPSTONE ENGINE"
)

# =========================================================
# API DETAILS
# =========================================================

API_KEY = "2fny2gd8v1yxolco"

# =========================================================
# TELEGRAM SETTINGS
# =========================================================

TELEGRAM_BOT_TOKEN = (
    "8321521772:AAF9uaNbjfDiok5P68Y0UXSL1K4aNsMZp6c"
)

TELEGRAM_CHAT_ID = (
    "8821072202"
)

# =========================================================
# ACCESS TOKEN CHECK
# =========================================================

if not os.path.exists(
    "access_token.txt"
):

    st.error(
        "RUN access.py FIRST"
    )

    st.stop()

# =========================================================
# READ ACCESS TOKEN
# =========================================================

with open(
    "access_token.txt",
    "r"
) as f:

    ACCESS_TOKEN = (
        f.read().strip()
    )

# =========================================================
# KITE LOGIN
# =========================================================

kite = KiteConnect(
    api_key=API_KEY
)

try:

    kite.set_access_token(
        ACCESS_TOKEN
    )

    profile = kite.profile()

    st.success(
        f"CONNECTED : "
        f"{profile['user_name']}"
    )

except Exception as e:

    st.error(
        f"KITE LOGIN ERROR : {e}"
    )

    st.stop()

# =========================================================
# TELEGRAM FUNCTION
# =========================================================

def send_telegram_message(
    message
):

    try:

        url = (

            f"https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}"
            f"/sendMessage"

        )

        payload = {

            "chat_id":
            TELEGRAM_CHAT_ID,

            "text":
            message

        }

        requests.post(
            url,
            data=payload,
            timeout=10
        )

    except Exception as e:

        print(
            f"TELEGRAM ERROR : {e}"
        )

# =========================================================
# LOAD CSV
# =========================================================

try:

    csv_df = pd.read_csv(
        "nifty_stocks.csv"
    )

    # =====================================
    # COLUMN CHECK
    # =====================================

    if "Stock" not in csv_df.columns:

        st.error(
            "CSV MUST CONTAIN "
            "'Stock' COLUMN"
        )

        st.stop()

    stock_names = (
        csv_df["Stock"]
        .dropna()
        .unique()
        .tolist()
    )

except Exception as e:

    st.error(
        f"CSV ERROR : {e}"
    )

    st.stop()

# =========================================================
# NSE INSTRUMENTS
# =========================================================

try:

    all_instruments = (
        kite.instruments("NSE")
    )

    instrument_df = pd.DataFrame(
        all_instruments
    )

except Exception as e:

    st.error(
        f"NSE ERROR : {e}"
    )

    st.stop()

# =========================================================
# STOCK TOKEN MAP
# =========================================================

NIFTY50 = {}

for stock in stock_names:

    try:

        row = instrument_df[

            instrument_df[
                "tradingsymbol"
            ] == stock

        ]

        if not row.empty:

            token = int(

                row.iloc[0][
                    "instrument_token"
                ]

            )

            NIFTY50[stock] = token

    except:

        pass

# =========================================================
# STOCK COUNT
# =========================================================

st.write(

    f"TOTAL STOCKS LOADED : "
    f"{len(NIFTY50)}"

)

# =========================================================
# MCX INSTRUMENTS
# =========================================================

try:

    mcx_instruments = (
        kite.instruments("MCX")
    )

    mcx_df = pd.DataFrame(
        mcx_instruments
    )

except Exception as e:

    st.error(
        f"MCX ERROR : {e}"
    )

    st.stop()

# =========================================================
# MCX SYMBOLS
# =========================================================

MCX_SYMBOLS = {

    "CRUDEOIL":
    "CRUDEOIL",

    "NATURALGAS":
    "NATURALGAS",

    "GOLDM":
    "GOLDM",

    "SILVERM":
    "SILVERM"
}

# =========================================================
# MCX TOKEN MAP
# =========================================================

MCX_TOKENS = {}

for key, search_symbol in (
    MCX_SYMBOLS.items()
):

    try:

        filtered = mcx_df[

            mcx_df[
                "tradingsymbol"
            ].str.contains(
                search_symbol,
                na=False
            )

        ]

        if not filtered.empty:

            filtered = (
                filtered
                .sort_values("expiry")
            )

            row = filtered.iloc[0]

            MCX_TOKENS[key] = {

                "symbol":
                row["tradingsymbol"],

                "token":
                int(
                    row[
                        "instrument_token"
                    ]
                )
            }

    except:

        pass

# =========================================================
# MCX DISPLAY
# =========================================================

st.write(
    "MCX CONTRACTS"
)

st.write(MCX_TOKENS)

# =========================================================
# NIFTY WEIGHTS
# =========================================================

NIFTY_WEIGHTS = {

    "RELIANCE": 10.5,
    "HDFCBANK": 8.9,
    "ICICIBANK": 7.8,
    "INFY": 6.5,
    "TCS": 5.2,
    "ITC": 4.3,
    "LT": 4.0,
    "SBIN": 3.8,
    "BHARTIARTL": 3.5,
    "AXISBANK": 3.2
}

# =========================================================
# SENSEX WEIGHTS
# =========================================================

SENSEX_WEIGHTS = {

    "RELIANCE": 11.2,
    "HDFCBANK": 10.1,
    "ICICIBANK": 8.5,
    "INFY": 7.2,
    "TCS": 6.1,
    "ITC": 4.5,
    "LT": 4.2,
    "SBIN": 3.7,
    "BHARTIARTL": 3.6,
    "AXISBANK": 3.1
}

# =========================================================
# SECTOR MAP
# =========================================================

SECTOR_MAP = {

    # =====================================
    # BANKING
    # =====================================

    "HDFCBANK": "BANKING",
    "ICICIBANK": "BANKING",
    "SBIN": "BANKING",
    "AXISBANK": "BANKING",
    "KOTAKBANK": "BANKING",

    # =====================================
    # IT
    # =====================================

    "INFY": "IT",
    "TCS": "IT",
    "HCLTECH": "IT",
    "WIPRO": "IT",

    # =====================================
    # ENERGY
    # =====================================

    "RELIANCE": "ENERGY",
    "ONGC": "ENERGY",

    # =====================================
    # FMCG
    # =====================================

    "ITC": "FMCG",
    "HINDUNILVR": "FMCG",

    # =====================================
    # PHARMA
    # =====================================

    "SUNPHARMA": "PHARMA",
    "DRREDDY": "PHARMA",

    # =====================================
    # AUTO
    # =====================================

    "MARUTI": "AUTO",
    "TATAMOTORS": "AUTO"
}

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title(
    "CAPSTONE FILTERS"
)

# =========================================================
# SIGNAL FILTER
# =========================================================

signal_filter = (
    st.sidebar.multiselect(

        "SIGNAL FILTER",

        [
            "BUY",
            "SELL",
            "NONE"
        ],

        default=[
            "BUY",
            "SELL",
            "NONE"
        ]
    )
)

# =========================================================
# SCORE FILTER
# =========================================================

min_score = (
    st.sidebar.slider(

        "MIN SCORE",

        -200,
        200,
        40
    )
)

# =========================================================
# RSI FILTER
# =========================================================

rsi_filter = (
    st.sidebar.slider(

        "RSI FILTER",

        0,
        100,
        62
    )
)

# =========================================================
# BB FILTER
# =========================================================

bb_filter = (
    st.sidebar.slider(

        "BB WIDTH FILTER",

        0,
        50,
        5
    )
)

# =========================================================
# DPO FILTER
# =========================================================

dpo_filter = (
    st.sidebar.slider(

        "DPO FILTER",

        0,
        8,
        6
    )
)

# =========================================================
# MACD FILTER
# =========================================================

macd_filter = (
    st.sidebar.slider(

        "MACD BULL COUNT",

        0,
        7,
        4
    )
)

# =========================================================
# DMI FILTER
# =========================================================

dmi_filter = (
    st.sidebar.slider(

        "DMI BULL COUNT",

        0,
        5,
        3
    )
)

# =========================================================
# SECTOR FILTER
# =========================================================

sector_filter = (
    st.sidebar.multiselect(

        "SECTOR FILTER",

        [
            "BANKING",
            "IT",
            "ENERGY",
            "FMCG",
            "PHARMA",
            "AUTO",
            "OTHERS"
        ],

        default=[
            "BANKING",
            "IT",
            "ENERGY",
            "FMCG",
            "PHARMA",
            "AUTO",
            "OTHERS"
        ]
    )
)

# =========================================================
# BREADTH FILTER
# =========================================================

breadth_mode = (
    st.sidebar.selectbox(

        "BREADTH MODE",

        [
            "ALL",
            "ONLY BULLISH",
            "ONLY BEARISH"
        ]
    )
)

# =========================================================
# TOP FILTER
# =========================================================

top_limit = (
    st.sidebar.slider(

        "TOP STOCK LIMIT",

        10,
        100,
        20
    )
)

# =========================================================
# AUTO REFRESH
# =========================================================

refresh_time = (
    st.sidebar.slider(

        "AUTO REFRESH (SEC)",

        30,
        300,
        60
    )
)

# =========================================================
# PART 2
# DATA FETCH + INDICATORS + RIBBON ENGINE
# =========================================================

# =========================================================
# FETCH DATA
# =========================================================

def get_data(
    token,
    interval="5minute"
):

    try:

        from_date = (

            datetime.now()
            -
            timedelta(days=30)

        )

        to_date = (
            datetime.now()
        )

        data = kite.historical_data(

            instrument_token=token,

            from_date=from_date,

            to_date=to_date,

            interval=interval,

            continuous=False,

            oi=False
        )

        # =====================================
        # EMPTY CHECK
        # =====================================

        if len(data) == 0:

            return pd.DataFrame()

        # =====================================
        # DATAFRAME
        # =====================================

        df = pd.DataFrame(data)

        # =====================================
        # INDEX
        # =====================================

        df.set_index(
            "date",
            inplace=True
        )

        # =====================================
        # CLEAN
        # =====================================

        df.dropna(inplace=True)

        return df

    except Exception as e:

        st.error(
            f"DATA ERROR : {e}"
        )

        return pd.DataFrame()

# =========================================================
# INDICATOR ENGINE
# =========================================================

def add_indicators(df):

    close = df["close"]

    high = df["high"]

    low = df["low"]

    volume = df["volume"]

    # =====================================================
    # MA RIBBON
    # =====================================================

    ma_periods = [

        4,6,8,10,
        12,14,16,
        18,20,22,
        24,26,28,
        30

    ]

    for p in ma_periods:

        df[f"ma_{p}"] = (

            close
            .rolling(p)
            .mean()

        )

    # =====================================================
    # MA ANGLE
    # =====================================================

    df["ma_angle"] = (

        df["ma_4"]
        -
        df["ma_20"]

    )

    # =====================================================
    # MA COMPRESSION
    # =====================================================

    df["ma_compression"] = (

        abs(
            df["ma_4"]
            -
            df["ma_30"]
        )

    )

    # =====================================================
    # RSI RIBBON
    # =====================================================

    rsi_periods = [

        25,
        30,
        35,
        40,
        45,
        50

    ]

    for p in rsi_periods:

        df[f"rsi_{p}"] = (

            ta.momentum
            .RSIIndicator(
                close,
                window=p
            )
            .rsi()

        )

    # =====================================================
    # RSI FORCE
    # =====================================================

    df["rsi_bull_count"] = 0

    df["rsi_bear_count"] = 0

    for p in rsi_periods:

        df["rsi_bull_count"] += np.where(

            df[f"rsi_{p}"] > 62,

            1,

            0

        )

        df["rsi_bear_count"] += np.where(

            df[f"rsi_{p}"] < 43,

            1,

            0

        )

    # =====================================================
    # DMI RIBBON
    # =====================================================

    dmi_periods = [

        10,
        15,
        20,
        25,
        30

    ]

    for p in dmi_periods:

        adx = ta.trend.ADXIndicator(

            high=high,

            low=low,

            close=close,

            window=p

        )

        df[f"di_pos_{p}"] = (
            adx.adx_pos()
        )

        df[f"di_neg_{p}"] = (
            adx.adx_neg()
        )

        df[f"adx_{p}"] = (
            adx.adx()
        )

    # =====================================================
    # DMI FORCE
    # =====================================================

    df["dmi_bull_count"] = 0

    df["dmi_bear_count"] = 0

    for p in dmi_periods:

        df["dmi_bull_count"] += np.where(

            df[f"di_pos_{p}"]
            >
            df[f"di_neg_{p}"],

            1,

            0

        )

        df["dmi_bear_count"] += np.where(

            df[f"di_pos_{p}"]
            <
            df[f"di_neg_{p}"],

            1,

            0

        )

    # =====================================================
    # MACD RIBBON
    # =====================================================

    macd_fast = [

        40,
        50,
        60,
        70,
        80,
        90,
        100

    ]

    for f in macd_fast:

        macd = ta.trend.MACD(

            close,

            window_fast=f,

            window_slow=f+10,

            window_sign=9

        )

        df[f"macd_{f}"] = (
            macd.macd()
        )

    # =====================================================
    # MACD FORCE
    # =====================================================

    df["macd_bull_count"] = 0

    df["macd_bear_count"] = 0

    for f in macd_fast:

        df["macd_bull_count"] += np.where(

            df[f"macd_{f}"] > 0,

            1,

            0

        )

        df["macd_bear_count"] += np.where(

            df[f"macd_{f}"] < 0,

            1,

            0

        )

    # =====================================================
    # DPO RIBBON
    # =====================================================

    dpo_periods = [

        12,
        20,
        25,
        30,
        35,
        40,
        45,
        50

    ]

    for p in dpo_periods:

        dpo = ta.trend.DPOIndicator(

            close,

            window=p

        )

        df[f"dpo_{p}"] = (
            dpo.dpo()
        )

    # =====================================================
    # DPO FORCE
    # =====================================================

    df["dpo_bull_count"] = 0

    df["dpo_bear_count"] = 0

    for p in dpo_periods:

        df["dpo_bull_count"] += np.where(

            df[f"dpo_{p}"] > 0,

            1,

            0

        )

        df["dpo_bear_count"] += np.where(

            df[f"dpo_{p}"] < 0,

            1,

            0

        )

    # =====================================================
    # DPO SLOPE
    # =====================================================

    df["dpo_slope"] = (

        df["dpo_12"]
        -
        df["dpo_50"]

    )

    # =====================================================
    # BOLLINGER BANDS
    # =====================================================

    bb = ta.volatility.BollingerBands(
        close
    )

    df["bb_upper"] = (
        bb.bollinger_hband()
    )

    df["bb_lower"] = (
        bb.bollinger_lband()
    )

    # =====================================================
    # BB WIDTH
    # =====================================================

    df["bb_width"] = (

        (
            df["bb_upper"]
            -
            df["bb_lower"]
        )

        /

        df["bb_upper"]

    ) * 100

    # =====================================================
    # ATR
    # =====================================================

    atr = ta.volatility.AverageTrueRange(

        high=high,

        low=low,

        close=close,

        window=14

    )

    df["atr"] = (
        atr.average_true_range()
    )

    # =====================================================
    # VWAP
    # =====================================================

    vwap = ta.volume.VolumeWeightedAveragePrice(

        high=high,

        low=low,

        close=close,

        volume=volume

    )

    df["vwap"] = (
        vwap.volume_weighted_average_price()
    )

    # =====================================================
    # VWAP POSITION
    # =====================================================

    df["above_vwap"] = np.where(

        close > df["vwap"],

        1,

        0

    )

    # =====================================================
    # VOLUME FORCE
    # =====================================================

    df["vol_ma"] = (
        volume
        .rolling(20)
        .mean()
    )

    df["volume_force"] = np.where(

        volume > df["vol_ma"],

        1,

        0

    )

    # =====================================================
    # MOMENTUM
    # =====================================================

    df["momentum"] = (
        close.diff(10)
    )

    # =====================================================
    # TREND FORCE
    # =====================================================

    df["trend_force"] = (

        df["rsi_bull_count"]

        +

        df["dmi_bull_count"]

        +

        df["macd_bull_count"]

        +

        df["dpo_bull_count"]

    )

    # =====================================================
    # BEAR FORCE
    # =====================================================

    df["bear_force"] = (

        df["rsi_bear_count"]

        +

        df["dmi_bear_count"]

        +

        df["macd_bear_count"]

        +

        df["dpo_bear_count"]

    )

    # =====================================================
    # CLEAN
    # =====================================================

    df.dropna(inplace=True)

    return df

# =========================================================
# SCORE ENGINE
# =========================================================

def calculate_score(df):

    latest = df.iloc[-1]

    score = 0

    # =====================================================
    # MA STRUCTURE
    # =====================================================

    if (

        latest["ma_4"]

        >

        latest["ma_10"]

        >

        latest["ma_20"]

    ):

        score += 20

    elif (

        latest["ma_4"]

        <

        latest["ma_10"]

        <

        latest["ma_20"]

    ):

        score -= 20

    # =====================================================
    # MA ANGLE
    # =====================================================

    if latest["ma_angle"] > 0:

        score += 10

    elif latest["ma_angle"] < 0:

        score -= 10

    # =====================================================
    # RSI FORCE
    # =====================================================

    if latest["rsi_bull_count"] >= 4:

        score += 15

    elif latest["rsi_bear_count"] >= 4:

        score -= 15

    # =====================================================
    # DMI FORCE
    # =====================================================

    if latest["dmi_bull_count"] >= 3:

        score += 15

    elif latest["dmi_bear_count"] >= 3:

        score -= 15

    # =====================================================
    # MACD FORCE
    # =====================================================

    if latest["macd_bull_count"] >= 4:

        score += 20

    elif latest["macd_bear_count"] >= 4:

        score -= 20

    # =====================================================
    # DPO FORCE
    # =====================================================

    if latest["dpo_bull_count"] >= 6:

        score += 20

    elif latest["dpo_bear_count"] >= 6:

        score -= 20

    # =====================================================
    # DPO SLOPE
    # =====================================================

    if latest["dpo_slope"] > 0:

        score += 10

    elif latest["dpo_slope"] < 0:

        score -= 10

    # =====================================================
    # BB WIDTH
    # =====================================================

    if latest["bb_width"] > 5:

        score += 5

    # =====================================================
    # VWAP
    # =====================================================

    if latest["above_vwap"] == 1:

        score += 5

    else:

        score -= 5

    # =====================================================
    # VOLUME FORCE
    # =====================================================

    if latest["volume_force"] == 1:

        score += 5

    # =====================================================
    # MOMENTUM
    # =====================================================

    if latest["momentum"] > 0:

        score += 5

    elif latest["momentum"] < 0:

        score -= 5

    # =====================================================
    # FINAL SIGNAL
    # =====================================================

    if score >= 80:

        signal = "STRONG BUY"

    elif score >= 40:

        signal = "BUY"

    elif score <= -80:

        signal = "STRONG SELL"

    elif score <= -40:

        signal = "SELL"

    else:

        signal = "NONE"

    return signal, score

# =========================================================
# PART 3
# STOCK ANALYSIS + INDEX FORCE + MCX ENGINE
# =========================================================

# =========================================================
# ANALYZE STOCK
# =========================================================

def analyze_stock(
    name,
    token
):

    try:

        # =================================================
        # 5m ENGINE
        # =================================================

        df5 = get_data(

            token,

            interval="5minute"

        )

        if df5.empty:

            return None

        df5 = add_indicators(df5)

        signal5, score5 = (
            calculate_score(df5)
        )

        latest5 = df5.iloc[-1]

        # =================================================
        # 15m ENGINE
        # =================================================

        df15 = get_data(

            token,

            interval="15minute"

        )

        if df15.empty:

            return None

        df15 = add_indicators(df15)

        signal15, score15 = (
            calculate_score(df15)
        )

        latest15 = df15.iloc[-1]

        # =================================================
        # TOTAL SCORE
        # =================================================

        total_score = (

            score5
            +
            score15

        )

        # =================================================
        # FINAL SIGNAL
        # =================================================

        if (

            signal5 in [
                "BUY",
                "STRONG BUY"
            ]

            and

            signal15 in [
                "BUY",
                "STRONG BUY"
            ]

        ):

            final_signal = "BUY"

        elif (

            signal5 in [
                "SELL",
                "STRONG SELL"
            ]

            and

            signal15 in [
                "SELL",
                "STRONG SELL"
            ]

        ):

            final_signal = "SELL"

        else:

            final_signal = "NONE"

        # =================================================
        # SECTOR
        # =================================================

        sector = SECTOR_MAP.get(
            name,
            "OTHERS"
        )

        # =================================================
        # RETURN STRUCTURE
        # =================================================

        return {

            # =============================================
            # BASIC
            # =============================================

            "Stock":
            name,

            "Sector":
            sector,

            "5m Signal":
            signal5,

            "5m Score":
            score5,

            "15m Signal":
            signal15,

            "15m Score":
            score15,

            "Final Signal":
            final_signal,

            "Total Score":
            total_score,

            # =============================================
            # RSI
            # =============================================

            "RSI Bull":
            latest5[
                "rsi_bull_count"
            ],

            "RSI Bear":
            latest5[
                "rsi_bear_count"
            ],

            # =============================================
            # DMI
            # =============================================

            "DMI Bull":
            latest5[
                "dmi_bull_count"
            ],

            "DMI Bear":
            latest5[
                "dmi_bear_count"
            ],

            # =============================================
            # MACD
            # =============================================

            "MACD Bull":
            latest5[
                "macd_bull_count"
            ],

            "MACD Bear":
            latest5[
                "macd_bear_count"
            ],

            # =============================================
            # DPO
            # =============================================

            "DPO Bull":
            latest5[
                "dpo_bull_count"
            ],

            "DPO Bear":
            latest5[
                "dpo_bear_count"
            ],

            # =============================================
            # BB WIDTH
            # =============================================

            "BB Width":
            round(
                latest5[
                    "bb_width"
                ],
                2
            ),

            # =============================================
            # MA ANGLE
            # =============================================

            "MA Angle":
            round(
                latest5[
                    "ma_angle"
                ],
                2
            ),

            # =============================================
            # ATR
            # =============================================

            "ATR":
            round(
                latest5[
                    "atr"
                ],
                2
            ),

            # =============================================
            # VWAP
            # =============================================

            "VWAP":
            round(
                latest5[
                    "vwap"
                ],
                2
            ),

            # =============================================
            # VOLUME FORCE
            # =============================================

            "Volume Force":
            latest5[
                "volume_force"
            ],

            # =============================================
            # TREND FORCE
            # =============================================

            "Trend Force":
            latest5[
                "trend_force"
            ],

            # =============================================
            # BEAR FORCE
            # =============================================

            "Bear Force":
            latest5[
                "bear_force"
            ]

        }

    except Exception as e:

        st.error(
            f"{name} ERROR : {e}"
        )

        return None

# =========================================================
# INDEX FORCE ENGINE
# =========================================================

def calculate_index_strength(
    df,
    weights
):

    total_weight = 0

    weighted_score = 0

    bullish = 0

    bearish = 0

    # =====================================================
    # WEIGHT STRUCTURE
    # =====================================================

    for _, row in df.iterrows():

        stock = row["Stock"]

        if stock not in weights:

            continue

        weight = weights[stock]

        total_weight += weight

        weighted_score += (

            row["Total Score"]
            *
            weight

        )

        # =================================================
        # BREADTH
        # =================================================

        if row["Final Signal"] == "BUY":

            bullish += 1

        elif row["Final Signal"] == "SELL":

            bearish += 1

    # =====================================================
    # NO WEIGHT
    # =====================================================

    if total_weight == 0:

        return 0, "NONE"

    # =====================================================
    # INDEX SCORE
    # =====================================================

    index_score = (

        weighted_score
        /
        total_weight

    )

    # =====================================================
    # PARTICIPATION
    # =====================================================

    participation = (

        bullish
        -
        bearish

    )

    # =====================================================
    # FINAL FORCE
    # =====================================================

    final_score = (

        index_score
        +
        participation

    )

    # =====================================================
    # FINAL SIGNAL
    # =====================================================

    if final_score >= 100:

        signal = "STRONG BUY"

    elif final_score >= 50:

        signal = "BUY"

    elif final_score <= -100:

        signal = "STRONG SELL"

    elif final_score <= -50:

        signal = "SELL"

    else:

        signal = "NONE"

    return (

        round(final_score, 2),

        signal

    )

# =========================================================
# MAIN STOCK ENGINE
# =========================================================

results = []

progress = st.progress(0)

total = len(NIFTY50)

for i, (stock, token) in enumerate(

    NIFTY50.items()

):

    result = analyze_stock(

        stock,

        token

    )

    if result:

        results.append(result)

    progress.progress(
        (i + 1) / total
    )

# =========================================================
# DATAFRAME
# =========================================================

df = pd.DataFrame(results)

# =========================================================
# EMPTY CHECK
# =========================================================

if df.empty:

    st.error(
        "NO STOCK DATA RECEIVED"
    )

    st.stop()

# =========================================================
# NIFTY FORCE
# =========================================================

nifty_score, nifty_signal = (

    calculate_index_strength(

        df,

        NIFTY_WEIGHTS

    )

)

# =========================================================
# SENSEX FORCE
# =========================================================

sensex_score, sensex_signal = (

    calculate_index_strength(

        df,

        SENSEX_WEIGHTS

    )

)

# =========================================================
# SECTOR FORCE ENGINE
# =========================================================

sector_scores = {}

for sector in set(

    SECTOR_MAP.values()

):

    sector_df = df[

        df["Sector"] == sector

    ]

    if not sector_df.empty:

        sector_scores[sector] = round(

            sector_df[
                "Total Score"
            ].mean(),

            2
        )

# =========================================================
# SECTOR DATAFRAME
# =========================================================

sector_display = pd.DataFrame(

    list(
        sector_scores.items()
    ),

    columns=[
        "Sector",
        "Force"
    ]
)

# =========================================================
# MCX ENGINE
# =========================================================

mcx_results = []

for name, data in (

    MCX_TOKENS.items()

):

    token = data["token"]

    symbol = data["symbol"]

    try:

        # =================================================
        # 5m ENGINE
        # =================================================

        df5 = get_data(

            token,

            interval="5minute"

        )

        if df5.empty:

            continue

        df5 = add_indicators(df5)

        signal5, score5 = (
            calculate_score(df5)
        )

        # =================================================
        # 15m ENGINE
        # =================================================

        df15 = get_data(

            token,

            interval="15minute"

        )

        if df15.empty:

            continue

        df15 = add_indicators(df15)

        signal15, score15 = (
            calculate_score(df15)
        )

        # =================================================
        # TOTAL SCORE
        # =================================================

        total_score = (

            score5
            +
            score15

        )

        # =================================================
        # FINAL SIGNAL
        # =================================================

        if (

            signal5 in [
                "BUY",
                "STRONG BUY"
            ]

            and

            signal15 in [
                "BUY",
                "STRONG BUY"
            ]

        ):

            final_signal = "BUY"

        elif (

            signal5 in [
                "SELL",
                "STRONG SELL"
            ]

            and

            signal15 in [
                "SELL",
                "STRONG SELL"
            ]

        ):

            final_signal = "SELL"

        else:

            final_signal = "NONE"

        # =================================================
        # APPEND
        # =================================================

        mcx_results.append({

            "Commodity":
            symbol,

            "5m Signal":
            signal5,

            "5m Score":
            score5,

            "15m Signal":
            signal15,

            "15m Score":
            score15,

            "Final Signal":
            final_signal,

            "Total Score":
            total_score

        })

    except Exception as e:

        st.error(

            f"MCX ERROR : "
            f"{symbol} : {e}"

        )

# =========================================================
# MCX DATAFRAME
# =========================================================

mcx_df_display = pd.DataFrame(
    mcx_results
)

# =========================================================
# TOP BUY
# =========================================================

top_buy = (

    df.sort_values(

        "Total Score",

        ascending=False

    )

    .head(top_limit)

)

# =========================================================
# TOP SELL
# =========================================================

top_sell = (

    df.sort_values(

        "Total Score",

        ascending=True

    )

    .head(top_limit)

)

# =========================================================
# FILTERS
# =========================================================

filtered_df = df[

    (
        df["Final Signal"]
        .isin(signal_filter)
    )

    &

    (
        abs(
            df["Total Score"]
        )
        >= min_score
    )

    &

    (
        df["Sector"]
        .isin(sector_filter)
    )

]

# =========================================================
# PART 4
# CAPSTONE DASHBOARD + HEATMAP + FILTERS
# =========================================================

# =========================================================
# MARKET STRUCTURE DASHBOARD
# =========================================================

st.markdown("---")

st.subheader(
    "INSTITUTIONAL MARKET STRUCTURE"
)

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "NIFTY FORCE",
        nifty_score
    )

with c2:

    st.metric(
        "NIFTY SIGNAL",
        nifty_signal
    )

with c3:

    st.metric(
        "SENSEX FORCE",
        sensex_score
    )

with c4:

    st.metric(
        "SENSEX SIGNAL",
        sensex_signal
    )

# =========================================================
# MOMENTUM LEADERS
# =========================================================

st.markdown("---")

st.subheader(
    "LIVE MOMENTUM LEADERS"
)

leader1, leader2, leader3, leader4 = (
    st.columns(4)
)

best_stock = (

    df.sort_values(
        "Total Score",
        ascending=False
    )

    .iloc[0]

)

worst_stock = (

    df.sort_values(
        "Total Score",
        ascending=True
    )

    .iloc[0]

)

with leader1:

    st.metric(

        "TOP BULLISH",

        best_stock["Stock"],

        best_stock["Total Score"]

    )

with leader2:

    st.metric(

        "TOP BEARISH",

        worst_stock["Stock"],

        worst_stock["Total Score"]

    )

with leader3:

    st.metric(

        "BULLISH STOCKS",

        len(
            df[
                df["Final Signal"]
                == "BUY"
            ]
        )
    )

with leader4:

    st.metric(

        "BEARISH STOCKS",

        len(
            df[
                df["Final Signal"]
                == "SELL"
            ]
        )
    )

# =========================================================
# SECTOR FORCE
# =========================================================

st.markdown("---")

st.subheader(
    "SECTOR FORCE DASHBOARD"
)

if not sector_display.empty:

    st.dataframe(

        sector_display.sort_values(

            "Force",

            ascending=False

        ),

        use_container_width=True,

        height=300

    )

# =========================================================
# ADVANCED FILTERS
# =========================================================

st.markdown("---")

st.subheader(
    "ADVANCED FILTERED VIEW"
)

advanced_filtered_df = filtered_df[

    (
        filtered_df["BB Width"]
        >= bb_filter
    )

    &

    (
        filtered_df["DPO Bull"]
        >= dpo_filter
    )

    &

    (
        filtered_df["MACD Bull"]
        >= macd_filter
    )

    &

    (
        filtered_df["DMI Bull"]
        >= dmi_filter
    )

]

# =========================================================
# BREADTH FILTER
# =========================================================

if breadth_mode == "ONLY BULLISH":

    advanced_filtered_df = (

        advanced_filtered_df[

            advanced_filtered_df[
                "Final Signal"
            ] == "BUY"

        ]

    )

elif breadth_mode == "ONLY BEARISH":

    advanced_filtered_df = (

        advanced_filtered_df[

            advanced_filtered_df[
                "Final Signal"
            ] == "SELL"

        ]

    )

# =========================================================
# HEATMAP TABLE
# =========================================================

st.dataframe(

    advanced_filtered_df
    .sort_values(
        "Total Score",
        ascending=False
    ),

    use_container_width=True,

    height=700
)

# =========================================================
# TOP 20 DASHBOARD
# =========================================================

st.markdown("---")

st.subheader(
    "TOP STOCK DASHBOARD"
)

col1, col2 = st.columns(2)

# =========================================================
# TOP BUY
# =========================================================

with col1:

    st.subheader(
        "TOP CALL SIDE"
    )

    st.dataframe(

        top_buy[

            [

                "Stock",
                "Sector",

                "5m Signal",
                "5m Score",

                "15m Signal",
                "15m Score",

                "Final Signal",

                "Total Score",

                "RSI Bull",
                "DMI Bull",
                "MACD Bull",
                "DPO Bull",

                "BB Width",

                "MA Angle",

                "ATR",

                "Trend Force"

            ]

        ],

        use_container_width=True,

        height=750
    )

# =========================================================
# TOP SELL
# =========================================================

with col2:

    st.subheader(
        "TOP PUT SIDE"
    )

    st.dataframe(

        top_sell[

            [

                "Stock",
                "Sector",

                "5m Signal",
                "5m Score",

                "15m Signal",
                "15m Score",

                "Final Signal",

                "Total Score",

                "RSI Bear",
                "DMI Bear",
                "MACD Bear",
                "DPO Bear",

                "BB Width",

                "MA Angle",

                "ATR",

                "Bear Force"

            ]

        ],

        use_container_width=True,

        height=750
    )

# =========================================================
# MCX DASHBOARD
# =========================================================

st.markdown("---")

st.subheader(
    "MCX INSTITUTIONAL DASHBOARD"
)

if not mcx_df_display.empty:

    st.dataframe(

        mcx_df_display.sort_values(

            "Total Score",

            ascending=False

        ),

        use_container_width=True,

        height=400
    )

else:

    st.warning(
        "NO MCX DATA"
    )

# =========================================================
# MARKET BREADTH
# =========================================================

st.markdown("---")

st.subheader(
    "MARKET BREADTH"
)

breadth1, breadth2, breadth3, breadth4 = (
    st.columns(4)
)

bullish_count = len(

    df[
        df["Final Signal"]
        == "BUY"
    ]

)

bearish_count = len(

    df[
        df["Final Signal"]
        == "SELL"
    ]

)

neutral_count = len(

    df[
        df["Final Signal"]
        == "NONE"
    ]

)

strong_buy_count = len(

    df[
        df["Total Score"]
        >= 100
    ]

)

with breadth1:

    st.metric(
        "BULLISH",
        bullish_count
    )

with breadth2:

    st.metric(
        "BEARISH",
        bearish_count
    )

with breadth3:

    st.metric(
        "NEUTRAL",
        neutral_count
    )

with breadth4:

    st.metric(
        "STRONG BULLISH",
        strong_buy_count
    )

# =========================================================
# FORCE DISTRIBUTION
# =========================================================

st.markdown("---")

st.subheader(
    "FORCE DISTRIBUTION"
)

force1, force2, force3 = (
    st.columns(3)
)

with force1:

    st.metric(

        "AVG TREND FORCE",

        round(
            df[
                "Trend Force"
            ].mean(),
            2
        )
    )

with force2:

    st.metric(

        "AVG BEAR FORCE",

        round(
            df[
                "Bear Force"
            ].mean(),
            2
        )
    )

with force3:

    st.metric(

        "AVG BB WIDTH",

        round(
            df[
                "BB Width"
            ].mean(),
            2
        )
    )

# =========================================================
# FULL MARKET TABLE
# =========================================================

st.markdown("---")

st.subheader(
    "FULL MARKET STRUCTURE TABLE"
)

st.dataframe(

    df.sort_values(

        "Total Score",

        ascending=False

    ),

    use_container_width=True,

    height=1000
)

# =========================================================
# PART 5
# TELEGRAM ALERTS + ALERT ENGINE + LIVE SCANNER
# =========================================================

# =========================================================
# LIVE ALERT ENGINE
# =========================================================

st.markdown("---")

st.subheader(
    "LIVE ALERT ENGINE"
)

alerts = []

# =========================================================
# STOCK ALERTS
# =========================================================

for _, row in df.iterrows():

    # =====================================================
    # STRONG BUY
    # =====================================================

    if row["Total Score"] >= 100:

        alert = (

            f"🚀 STRONG BUY ALERT 🚀\n\n"

            f"STOCK : {row['Stock']}\n"

            f"SECTOR : {row['Sector']}\n\n"

            f"5m : "
            f"{row['5m Signal']} | "
            f"{row['5m Score']}\n"

            f"15m : "
            f"{row['15m Signal']} | "
            f"{row['15m Score']}\n\n"

            f"TOTAL SCORE : "
            f"{row['Total Score']}\n\n"

            f"RSI BULL : "
            f"{row['RSI Bull']}\n"

            f"DMI BULL : "
            f"{row['DMI Bull']}\n"

            f"MACD BULL : "
            f"{row['MACD Bull']}\n"

            f"DPO BULL : "
            f"{row['DPO Bull']}\n\n"

            f"BB WIDTH : "
            f"{row['BB Width']}\n"

            f"MA ANGLE : "
            f"{row['MA Angle']}\n"

            f"ATR : "
            f"{row['ATR']}\n"

            f"TREND FORCE : "
            f"{row['Trend Force']}"
        )

        alerts.append(alert)

        send_telegram_message(
            alert
        )

    # =====================================================
    # STRONG SELL
    # =====================================================

    elif row["Total Score"] <= -100:

        alert = (

            f"🔻 STRONG SELL ALERT 🔻\n\n"

            f"STOCK : {row['Stock']}\n"

            f"SECTOR : {row['Sector']}\n\n"

            f"5m : "
            f"{row['5m Signal']} | "
            f"{row['5m Score']}\n"

            f"15m : "
            f"{row['15m Signal']} | "
            f"{row['15m Score']}\n\n"

            f"TOTAL SCORE : "
            f"{row['Total Score']}\n\n"

            f"RSI BEAR : "
            f"{row['RSI Bear']}\n"

            f"DMI BEAR : "
            f"{row['DMI Bear']}\n"

            f"MACD BEAR : "
            f"{row['MACD Bear']}\n"

            f"DPO BEAR : "
            f"{row['DPO Bear']}\n\n"

            f"BB WIDTH : "
            f"{row['BB Width']}\n"

            f"MA ANGLE : "
            f"{row['MA Angle']}\n"

            f"ATR : "
            f"{row['ATR']}\n"

            f"BEAR FORCE : "
            f"{row['Bear Force']}"
        )

        alerts.append(alert)

        send_telegram_message(
            alert
        )

# =========================================================
# MCX ALERT ENGINE
# =========================================================

for _, row in mcx_df_display.iterrows():

    # =====================================================
    # MCX BUY
    # =====================================================

    if row["Total Score"] >= 100:

        mcx_alert = (

            f"🔥 MCX BUY ALERT 🔥\n\n"

            f"{row['Commodity']}\n\n"

            f"5m : "
            f"{row['5m Signal']} | "
            f"{row['5m Score']}\n"

            f"15m : "
            f"{row['15m Signal']} | "
            f"{row['15m Score']}\n\n"

            f"FINAL : "
            f"{row['Final Signal']}\n"

            f"TOTAL SCORE : "
            f"{row['Total Score']}"
        )

        send_telegram_message(
            mcx_alert
        )

    # =====================================================
    # MCX SELL
    # =====================================================

    elif row["Total Score"] <= -100:

        mcx_alert = (

            f"⚠️ MCX SELL ALERT ⚠️\n\n"

            f"{row['Commodity']}\n\n"

            f"5m : "
            f"{row['5m Signal']} | "
            f"{row['5m Score']}\n"

            f"15m : "
            f"{row['15m Signal']} | "
            f"{row['15m Score']}\n\n"

            f"FINAL : "
            f"{row['Final Signal']}\n"

            f"TOTAL SCORE : "
            f"{row['Total Score']}"
        )

        send_telegram_message(
            mcx_alert
        )

# =========================================================
# DISPLAY ALERTS
# =========================================================

if len(alerts) == 0:

    st.info(
        "NO EXTREME ALERTS"
    )

else:

    for alert in alerts:

        st.warning(alert)

# =========================================================
# LIVE BREAKOUT SCANNER
# =========================================================

st.markdown("---")

st.subheader(
    "LIVE BREAKOUT SCANNER"
)

breakout_df = df[

    (
        df["BB Width"] > 5
    )

    &

    (
        df["Trend Force"] > 15
    )

]

if not breakout_df.empty:

    st.dataframe(

        breakout_df.sort_values(

            "Total Score",

            ascending=False

        ),

        use_container_width=True,

        height=500
    )

else:

    st.info(
        "NO BREAKOUTS FOUND"
    )

# =========================================================
# LIVE REVERSAL SCANNER
# =========================================================

st.markdown("---")

st.subheader(
    "LIVE REVERSAL SCANNER"
)

reversal_df = df[

    (
        abs(
            df["MA Angle"]
        ) < 1
    )

    &

    (
        df["BB Width"] > 4
    )

]

if not reversal_df.empty:

    st.dataframe(

        reversal_df.sort_values(

            "BB Width",

            ascending=False

        ),

        use_container_width=True,

        height=500
    )

else:

    st.info(
        "NO REVERSALS FOUND"
    )

# =========================================================
# INSTITUTIONAL FLOW SCANNER
# =========================================================

st.markdown("---")

st.subheader(
    "INSTITUTIONAL FLOW SCANNER"
)

flow_df = df[

    (
        df["Volume Force"] == 1
    )

    &

    (
        df["Trend Force"] > 10
    )

]

if not flow_df.empty:

    st.dataframe(

        flow_df.sort_values(

            "Trend Force",

            ascending=False

        ),

        use_container_width=True,

        height=500
    )

else:

    st.info(
        "NO FLOW FOUND"
    )

# =========================================================
# HIGH VOLATILITY SCANNER
# =========================================================

st.markdown("---")

st.subheader(
    "HIGH VOLATILITY SCANNER"
)

volatility_df = df[

    df["BB Width"] > 8

]

if not volatility_df.empty:

    st.dataframe(

        volatility_df.sort_values(

            "BB Width",

            ascending=False

        ),

        use_container_width=True,

        height=500
    )

else:

    st.info(
        "NO HIGH VOLATILITY"
    )

# =========================================================
# MOMENTUM CONTINUATION SCANNER
# =========================================================

st.markdown("---")

st.subheader(
    "MOMENTUM CONTINUATION"
)

momentum_df = df[

    (
        df["Trend Force"] > 18
    )

    &

    (
        df["Final Signal"] == "BUY"
    )

]

if not momentum_df.empty:

    st.dataframe(

        momentum_df.sort_values(

            "Trend Force",

            ascending=False

        ),

        use_container_width=True,

        height=500
    )

else:

    st.info(
        "NO MOMENTUM CONTINUATION"
    )

    # =========================================================
# PART 6
# FINAL DASHBOARD + AUTO REFRESH + SUMMARY ENGINE
# =========================================================

# =========================================================
# LIVE SUMMARY ENGINE
# =========================================================

st.markdown("---")

st.subheader(
    "LIVE MARKET SUMMARY"
)

summary1, summary2, summary3, summary4 = (
    st.columns(4)
)

# =========================================================
# MARKET DIRECTION
# =========================================================

market_direction = "SIDEWAYS"

if nifty_score > 50 and sensex_score > 50:

    market_direction = "STRONG BULLISH"

elif nifty_score < -50 and sensex_score < -50:

    market_direction = "STRONG BEARISH"

elif nifty_score > 20:

    market_direction = "BULLISH"

elif nifty_score < -20:

    market_direction = "BEARISH"

# =========================================================
# TREND STRENGTH
# =========================================================

avg_trend_force = round(

    df["Trend Force"].mean(),

    2

)

# =========================================================
# VOLATILITY
# =========================================================

avg_volatility = round(

    df["BB Width"].mean(),

    2

)

# =========================================================
# MOMENTUM
# =========================================================

avg_momentum = round(

    df["Total Score"].mean(),

    2

)

with summary1:

    st.metric(

        "MARKET DIRECTION",

        market_direction

    )

with summary2:

    st.metric(

        "AVG TREND FORCE",

        avg_trend_force

    )

with summary3:

    st.metric(

        "AVG VOLATILITY",

        avg_volatility

    )

with summary4:

    st.metric(

        "AVG MOMENTUM",

        avg_momentum

    )

# =========================================================
# MARKET INTERNALS
# =========================================================

st.markdown("---")

st.subheader(
    "MARKET INTERNALS"
)

internal1, internal2, internal3, internal4 = (
    st.columns(4)
)

# =========================================================
# ABOVE VWAP
# =========================================================

above_vwap_count = len(

    df[
        df["Trend Force"] > 10
    ]

)

# =========================================================
# BB EXPANSION
# =========================================================

bb_expansion_count = len(

    df[
        df["BB Width"] > 5
    ]

)

# =========================================================
# STRONG BULL
# =========================================================

strong_bull_count = len(

    df[
        df["Total Score"] >= 100
    ]

)

# =========================================================
# STRONG BEAR
# =========================================================

strong_bear_count = len(

    df[
        df["Total Score"] <= -100
    ]

)

with internal1:

    st.metric(
        "TREND STOCKS",
        above_vwap_count
    )

with internal2:

    st.metric(
        "BB EXPANSION",
        bb_expansion_count
    )

with internal3:

    st.metric(
        "STRONG BUY",
        strong_bull_count
    )

with internal4:

    st.metric(
        "STRONG SELL",
        strong_bear_count
    )

# =========================================================
# LIVE MCX SUMMARY
# =========================================================

st.markdown("---")

st.subheader(
    "MCX MARKET SUMMARY"
)

if not mcx_df_display.empty:

    mcx1, mcx2, mcx3, mcx4 = (
        st.columns(4)
    )

    best_mcx = (

        mcx_df_display
        .sort_values(
            "Total Score",
            ascending=False
        )
        .iloc[0]

    )

    worst_mcx = (

        mcx_df_display
        .sort_values(
            "Total Score",
            ascending=True
        )
        .iloc[0]

    )

    with mcx1:

        st.metric(

            "TOP MCX BUY",

            best_mcx[
                "Commodity"
            ],

            best_mcx[
                "Total Score"
            ]
        )

    with mcx2:

        st.metric(

            "TOP MCX SELL",

            worst_mcx[
                "Commodity"
            ],

            worst_mcx[
                "Total Score"
            ]
        )

    with mcx3:

        st.metric(

            "MCX BUY COUNT",

            len(

                mcx_df_display[

                    mcx_df_display[
                        "Final Signal"
                    ] == "BUY"

                ]

            )
        )

    with mcx4:

        st.metric(

            "MCX SELL COUNT",

            len(

                mcx_df_display[

                    mcx_df_display[
                        "Final Signal"
                    ] == "SELL"

                ]

            )
        )

# =========================================================
# LIVE WATCHLIST
# =========================================================

st.markdown("---")

st.subheader(
    "LIVE WATCHLIST"
)

watchlist_df = df[

    (
        abs(
            df["Total Score"]
        ) >= 80
    )

]

if not watchlist_df.empty:

    st.dataframe(

        watchlist_df.sort_values(

            "Total Score",

            ascending=False

        ),

        use_container_width=True,

        height=700
    )

else:

    st.info(
        "NO WATCHLIST STOCKS"
    )

# =========================================================
# EXPORT CSV
# =========================================================

st.markdown("---")

st.subheader(
    "EXPORT DATA"
)

csv_export = df.to_csv(
    index=False
)

st.download_button(

    label="DOWNLOAD MARKET DATA",

    data=csv_export,

    file_name=(
        "market_structure.csv"
    ),

    mime="text/csv"
)

# =========================================================
# LAST UPDATE
# =========================================================

st.markdown("---")

st.write(

    "LAST UPDATE : ",

    datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)

# =========================================================
# AUTO REFRESH INFO
# =========================================================

st.info(

    f"AUTO REFRESH EVERY "
    f"{refresh_time} SECONDS"

)

# =========================================================
# AUTO REFRESH
# =========================================================

time.sleep(refresh_time)

st.rerun()

