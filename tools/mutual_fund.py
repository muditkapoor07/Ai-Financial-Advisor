"""
Mutual fund tools using the MFAPI (https://www.mfapi.in) and AMFI data.
Free public APIs — no API key required.
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime


MFAPI_BASE       = "https://api.mfapi.in/mf"
AMFI_SEARCH_BASE = "https://api.mfapi.in/mf/search"
AMFI_ALL_URL     = "https://api.mfapi.in/mf"
REQUEST_TIMEOUT  = 15  # seconds


def _safe_get(url: str, params: Optional[dict] = None) -> Optional[dict]:
    """Make a GET request and return parsed JSON, or None on failure."""
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


# ─────────────────────────────────────────────
# NAV — current Net Asset Value
# ─────────────────────────────────────────────

def get_fund_nav(scheme_code: str) -> Dict[str, Any]:
    """
    Fetch the current NAV and basic details for a mutual fund.

    Parameters
    ----------
    scheme_code : AMFI scheme code (numeric string). Use search_funds() to find codes.
                  Example: '120503' for Axis Bluechip Fund.

    Returns
    -------
    Dict with fund name, NAV, date, fund house, and scheme type.
    """
    url  = f"{MFAPI_BASE}/{scheme_code}"
    data = _safe_get(url)

    if not data or "error" in data:
        return data or {"error": f"No data returned for scheme code '{scheme_code}'."}

    meta = data.get("meta", {})
    nav_data = data.get("data", [])

    if not nav_data:
        return {"error": f"NAV data not available for scheme '{scheme_code}'."}

    latest = nav_data[0]  # most recent NAV
    prev   = nav_data[1] if len(nav_data) > 1 else None

    nav_change     = None
    nav_change_pct = None
    if prev:
        try:
            nav_change     = round(float(latest["nav"]) - float(prev["nav"]), 4)
            nav_change_pct = round(nav_change / float(prev["nav"]) * 100, 4)
        except (ValueError, ZeroDivisionError):
            pass

    return {
        "scheme_code":   scheme_code,
        "scheme_name":   meta.get("scheme_name", "N/A"),
        "fund_house":    meta.get("fund_house", "N/A"),
        "scheme_type":   meta.get("scheme_type", "N/A"),
        "scheme_category": meta.get("scheme_category", "N/A"),
        "current_nav":   latest.get("nav", "N/A"),
        "nav_date":      latest.get("date", "N/A"),
        "nav_change":    nav_change,
        "nav_change_pct": f"{nav_change_pct:+.4f}%" if nav_change_pct is not None else "N/A",
        "previous_nav":  prev.get("nav", "N/A") if prev else "N/A",
        "previous_date": prev.get("date", "N/A") if prev else "N/A",
        "isin_growth":   meta.get("isin_growth", "N/A"),
        "isin_dividend": meta.get("isin_div_payout", "N/A"),
    }


# ─────────────────────────────────────────────
# Fund search
# ─────────────────────────────────────────────

def search_funds(query: str) -> Dict[str, Any]:
    """
    Search for mutual funds by name or keyword from the AMFI list.

    Parameters
    ----------
    query : Search string, e.g., 'axis bluechip', 'mirae emerging', 'nifty 50 index'

    Returns
    -------
    Dict with list of matching funds (scheme_code, scheme_name, fund_house).
    """
    url  = f"{AMFI_SEARCH_BASE}?q={query}"
    data = _safe_get(url)

    if not data or "error" in data:
        return data or {"error": "Search failed."}

    # API returns a list of {schemeCode, schemeName, fundHouse}
    if isinstance(data, list):
        results = []
        for item in data[:20]:  # cap at 20 results
            results.append({
                "scheme_code": str(item.get("schemeCode", "")),
                "scheme_name": item.get("schemeName", ""),
                "fund_house":  item.get("fundHouse", ""),
            })
        return {
            "query":   query,
            "count":   len(results),
            "results": results,
            "note":    "Use scheme_code with get_fund_nav() or get_fund_details() for more info.",
        }

    return {"error": "Unexpected API response format.", "raw": str(data)[:200]}


# ─────────────────────────────────────────────
# Fund details with historical NAV
# ─────────────────────────────────────────────

def get_fund_details(scheme_code: str) -> Dict[str, Any]:
    """
    Fetch full fund information plus historical NAV for performance analysis.

    Parameters
    ----------
    scheme_code : AMFI scheme code

    Returns
    -------
    Dict with NAV, 1-week/1-month/3-month/6-month/1-year/3-year/5-year returns,
    and metadata.
    """
    url  = f"{MFAPI_BASE}/{scheme_code}"
    data = _safe_get(url)

    if not data or "error" in data:
        return data or {"error": f"No data for scheme code '{scheme_code}'."}

    meta     = data.get("meta", {})
    nav_data = data.get("data", [])

    if not nav_data:
        return {"error": "No NAV history available."}

    # Parse NAV history
    def parse_nav(record):
        try:
            return float(record["nav"])
        except (KeyError, ValueError):
            return None

    def parse_date(record):
        try:
            return datetime.strptime(record["date"], "%d-%m-%Y")
        except (KeyError, ValueError):
            return None

    nav_pairs = [(parse_date(r), parse_nav(r)) for r in nav_data]
    nav_pairs = [(d, n) for d, n in nav_pairs if d is not None and n is not None]
    nav_pairs.sort(key=lambda x: x[0], reverse=True)  # most recent first

    if not nav_pairs:
        return {"error": "Could not parse NAV data."}

    latest_date, latest_nav = nav_pairs[0]

    def find_nav_near(target_date):
        """Find the NAV closest to target_date."""
        for dt, nav in nav_pairs:
            if dt <= target_date:
                return nav, dt
        return None, None

    def calc_return(nav_start, nav_end):
        if nav_start and nav_end and nav_start > 0:
            return round((nav_end - nav_start) / nav_start * 100, 2)
        return None

    # Calculate period returns
    returns = {}
    periods = {
        "1_week":   7,
        "1_month":  30,
        "3_months": 91,
        "6_months": 182,
        "1_year":   365,
        "3_years":  1095,
        "5_years":  1825,
    }
    for label, days in periods.items():
        past_date  = latest_date - __import__("datetime").timedelta(days=days)
        past_nav, past_nav_date = find_nav_near(past_date)
        ret = calc_return(past_nav, latest_nav)
        if ret is not None:
            # Annualise for periods > 1 year (CAGR)
            if days > 365 and past_nav:
                years  = days / 365
                cagr   = ((latest_nav / past_nav) ** (1 / years) - 1) * 100
                returns[label] = f"{round(cagr, 2)}% p.a. (CAGR)"
            else:
                returns[label] = f"{ret}%"
        else:
            returns[label] = "N/A"

    # Recent NAV table (last 15 days)
    recent_navs = [
        {"date": d.strftime("%d-%m-%Y"), "nav": n}
        for d, n in nav_pairs[:15]
    ]

    # 52-week stats
    navs_1y = [n for d, n in nav_pairs if (latest_date - d).days <= 365]
    high_1y  = round(max(navs_1y), 4) if navs_1y else None
    low_1y   = round(min(navs_1y), 4) if navs_1y else None

    return {
        "scheme_code":     scheme_code,
        "scheme_name":     meta.get("scheme_name", "N/A"),
        "fund_house":      meta.get("fund_house", "N/A"),
        "scheme_type":     meta.get("scheme_type", "N/A"),
        "scheme_category": meta.get("scheme_category", "N/A"),
        "isin_growth":     meta.get("isin_growth", "N/A"),
        "current_nav":     latest_nav,
        "nav_date":        latest_date.strftime("%d-%m-%Y"),
        "52w_high":        high_1y,
        "52w_low":         low_1y,
        "returns":         returns,
        "total_nav_records": len(nav_pairs),
        "fund_since":      nav_pairs[-1][0].strftime("%d-%m-%Y") if nav_pairs else "N/A",
        "recent_nav_history": recent_navs,
        "note": (
            "Returns > 1 year are CAGR. Past performance is not a guarantee of future returns. "
            "Mutual fund investments are subject to market risks."
        ),
    }
