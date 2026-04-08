"""
Stock data tools using yfinance.
Handles NSE (.NS) and BSE (.BO) symbols for Indian equities.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
# Single stock — current price & summary
# ─────────────────────────────────────────────

def get_stock_price(symbol: str) -> Dict[str, Any]:
    """
    Fetch the current price, day change, 52-week high/low, and key metrics
    for an NSE or BSE listed stock.

    Parameters
    ----------
    symbol : Stock symbol e.g. 'RELIANCE.NS', 'TCS.NS', 'INFY.BO'
             Append .NS for NSE, .BO for BSE. If no suffix is given,
             .NS is tried first, then .BO.

    Returns
    -------
    Dict with price, change, 52w high/low, market cap, P/E, etc.
    """
    # Auto-append .NS if no exchange suffix
    if "." not in symbol:
        symbol = symbol + ".NS"

    try:
        ticker = yf.Ticker(symbol)
        info   = ticker.info

        # yfinance may return an empty dict for invalid symbols
        if not info or info.get("regularMarketPrice") is None:
            # Try BSE fallback
            alt_sym = symbol.replace(".NS", ".BO")
            ticker  = yf.Ticker(alt_sym)
            info    = ticker.info
            if not info or info.get("regularMarketPrice") is None:
                return {
                    "error": f"Could not fetch data for symbol '{symbol}'. "
                             f"Ensure it is a valid NSE (.NS) or BSE (.BO) symbol."
                }
            symbol = alt_sym

        current_price  = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev_close     = info.get("previousClose") or info.get("regularMarketPreviousClose", 0)
        day_change     = current_price - prev_close if prev_close else 0
        day_change_pct = (day_change / prev_close * 100) if prev_close else 0

        market_cap     = info.get("marketCap", 0)
        market_cap_cr  = round(market_cap / 1e7, 2) if market_cap else None  # in crores

        return {
            "symbol":          symbol,
            "company_name":    info.get("longName") or info.get("shortName", symbol),
            "current_price":   round(current_price, 2),
            "previous_close":  round(prev_close, 2),
            "day_change":      round(day_change, 2),
            "day_change_pct":  f"{day_change_pct:+.2f}%",
            "open":            round(info.get("open") or info.get("regularMarketOpen", 0), 2),
            "day_high":        round(info.get("dayHigh") or info.get("regularMarketDayHigh", 0), 2),
            "day_low":         round(info.get("dayLow") or info.get("regularMarketDayLow", 0), 2),
            "week_52_high":    round(info.get("fiftyTwoWeekHigh", 0), 2),
            "week_52_low":     round(info.get("fiftyTwoWeekLow", 0), 2),
            "volume":          info.get("volume") or info.get("regularMarketVolume", 0),
            "avg_volume":      info.get("averageVolume", 0),
            "market_cap_crore": market_cap_cr,
            "pe_ratio":        round(info.get("trailingPE", 0) or 0, 2),
            "pb_ratio":        round(info.get("priceToBook", 0) or 0, 2),
            "dividend_yield":  f"{(info.get('dividendYield') or 0) * 100:.2f}%",
            "eps":             round(info.get("trailingEps", 0) or 0, 2),
            "beta":            round(info.get("beta", 0) or 0, 2),
            "sector":          info.get("sector", "N/A"),
            "industry":        info.get("industry", "N/A"),
            "exchange":        info.get("exchange", "NSE/BSE"),
            "currency":        info.get("currency", "INR"),
            "data_as_of":      datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    except Exception as e:
        return {
            "error":  f"Failed to fetch data for '{symbol}': {str(e)}",
            "symbol": symbol,
        }


# ─────────────────────────────────────────────
# Historical data
# ─────────────────────────────────────────────

def get_stock_history(
    symbol: str,
    period: str = "1y",
) -> Dict[str, Any]:
    """
    Fetch historical OHLCV data for a stock.

    Parameters
    ----------
    symbol : Stock symbol (e.g., 'TCS.NS')
    period : Data period. Valid values:
             '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'

    Returns
    -------
    Dict with OHLCV summary, returns, and key statistics.
    """
    if "." not in symbol:
        symbol = symbol + ".NS"

    try:
        ticker  = yf.Ticker(symbol)
        hist    = ticker.history(period=period)

        if hist.empty:
            return {"error": f"No historical data found for '{symbol}' with period '{period}'."}

        # Calculate returns
        start_price = hist["Close"].iloc[0]
        end_price   = hist["Close"].iloc[-1]
        total_return = ((end_price - start_price) / start_price) * 100

        # Annualised return (CAGR approximation)
        trading_days = len(hist)
        years_approx = trading_days / 252
        if years_approx > 0:
            cagr = ((end_price / start_price) ** (1 / years_approx) - 1) * 100
        else:
            cagr = total_return

        # Volatility (annualised std of daily returns)
        daily_returns = hist["Close"].pct_change().dropna()
        volatility    = daily_returns.std() * (252 ** 0.5) * 100

        # Max drawdown
        rolling_max   = hist["Close"].cummax()
        drawdown      = (hist["Close"] - rolling_max) / rolling_max
        max_drawdown  = drawdown.min() * 100

        # Build OHLCV table (last 10 rows for brevity)
        recent = hist.tail(10)[["Open", "High", "Low", "Close", "Volume"]].round(2)
        ohlcv_records = []
        for date, row in recent.iterrows():
            ohlcv_records.append({
                "date":   date.strftime("%Y-%m-%d"),
                "open":   round(row["Open"], 2),
                "high":   round(row["High"], 2),
                "low":    round(row["Low"], 2),
                "close":  round(row["Close"], 2),
                "volume": int(row["Volume"]),
            })

        return {
            "symbol":           symbol,
            "period":           period,
            "trading_days":     trading_days,
            "start_date":       hist.index[0].strftime("%Y-%m-%d"),
            "end_date":         hist.index[-1].strftime("%Y-%m-%d"),
            "start_price":      round(start_price, 2),
            "end_price":        round(end_price, 2),
            "total_return_pct": f"{total_return:+.2f}%",
            "cagr_pct":         f"{cagr:+.2f}%",
            "annualised_volatility": f"{volatility:.2f}%",
            "max_drawdown_pct": f"{max_drawdown:.2f}%",
            "period_high":      round(hist["High"].max(), 2),
            "period_low":       round(hist["Low"].min(), 2),
            "avg_volume":       int(hist["Volume"].mean()),
            "recent_10_sessions": ohlcv_records,
        }

    except Exception as e:
        return {"error": f"Failed to fetch history for '{symbol}': {str(e)}"}


# ─────────────────────────────────────────────
# Multiple stocks — batch fetch
# ─────────────────────────────────────────────

def get_multiple_stocks(symbols: List[str]) -> Dict[str, Any]:
    """
    Fetch current prices for multiple stocks in one call.

    Parameters
    ----------
    symbols : List of stock symbols e.g. ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']

    Returns
    -------
    Dict mapping symbol to its price data dict.
    """
    results = {}
    errors  = []

    for sym in symbols:
        data = get_stock_price(sym)
        if "error" in data:
            errors.append(data["error"])
            results[sym] = {"error": data["error"]}
        else:
            results[sym] = {
                "company_name":   data["company_name"],
                "current_price":  data["current_price"],
                "day_change":     data["day_change"],
                "day_change_pct": data["day_change_pct"],
                "week_52_high":   data["week_52_high"],
                "week_52_low":    data["week_52_low"],
                "pe_ratio":       data["pe_ratio"],
                "market_cap_crore": data["market_cap_crore"],
                "sector":         data["sector"],
            }

    return {
        "stocks":      results,
        "total_queried": len(symbols),
        "successful":  len(symbols) - len(errors),
        "errors":      errors,
        "data_as_of":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
