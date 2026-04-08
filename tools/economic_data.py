"""
Economic data tools using the World Bank API.
Fetches India CPI inflation, GDP growth, and other macro indicators.
"""

import requests
from typing import Dict, Any, List, Optional

WB_API_BASE     = "https://api.worldbank.org/v2"
REQUEST_TIMEOUT = 15
DEFAULT_YEARS   = 5   # how many recent years to fetch


# World Bank indicator codes
WB_INDICATORS = {
    "CPI_INFLATION":      "FP.CPI.TOTL.ZG",   # Consumer price inflation (%)
    "GDP_GROWTH":         "NY.GDP.MKTP.KD.ZG", # GDP growth (annual %)
    "GDP_CURRENT_USD":    "NY.GDP.MKTP.CD",    # GDP (current US$)
    "GDP_PER_CAPITA":     "NY.GDP.PCAP.CD",    # GDP per capita (current US$)
    "UNEMPLOYMENT":       "SL.UEM.TOTL.ZS",    # Unemployment (% of total labour force)
    "CURRENT_ACCOUNT":    "BN.CAB.XOKA.GD.ZS", # Current account balance (% of GDP)
    "FOREX_RESERVES":     "FI.RES.TOTL.CD",    # Total reserves (current US$)
    "REPO_RATE":          None,                # Not available on World Bank — use RBI
}


def _wb_fetch(indicator: str, country: str = "IN", years: int = DEFAULT_YEARS) -> Optional[list]:
    """Fetch data from World Bank API for a given indicator and country."""
    url = (
        f"{WB_API_BASE}/country/{country}/indicator/{indicator}"
        f"?format=json&per_page={years + 2}&mrv={years + 2}"
    )
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
        if isinstance(payload, list) and len(payload) >= 2:
            return payload[1]  # actual data is in second element
        return None
    except Exception:
        return None


def _format_wb_series(raw_data: Optional[list], unit: str = "%") -> Dict[str, Any]:
    """Convert raw World Bank data into a clean year→value dict."""
    if not raw_data:
        return {}
    result = {}
    for entry in raw_data:
        year  = entry.get("date")
        value = entry.get("value")
        if year and value is not None:
            result[year] = round(float(value), 2)
    return dict(sorted(result.items(), reverse=True))


# ─────────────────────────────────────────────
# Inflation
# ─────────────────────────────────────────────

def get_inflation_rate(country_code: str = "IN") -> Dict[str, Any]:
    """
    Fetch Consumer Price Inflation (CPI) data from the World Bank API.

    Parameters
    ----------
    country_code : ISO 3166-1 alpha-2 country code (default 'IN' for India).

    Returns
    -------
    Dict with 5-year CPI inflation series and key statistics.
    """
    raw = _wb_fetch(WB_INDICATORS["CPI_INFLATION"], country=country_code, years=DEFAULT_YEARS)

    if raw is None:
        return {
            "error":   "Could not fetch inflation data from World Bank API.",
            "country": country_code,
            "fallback_info": {
                "India_FY2024_estimated": "~5.4%",
                "India_FY2023": "~6.7%",
                "RBI_target": "4% (±2% band)",
                "source": "Estimated — World Bank data may have ~1-2 year lag",
            },
        }

    series = _format_wb_series(raw)
    if not series:
        return {"error": "No inflation data available.", "country": country_code}

    values       = list(series.values())
    latest_year  = list(series.keys())[0]
    latest_value = values[0]
    avg_5y       = round(sum(values) / len(values), 2) if values else None
    trend        = "Rising" if len(values) >= 2 and values[0] > values[1] else "Falling"

    rbi_context = {}
    if country_code.upper() == "IN":
        rbi_context = {
            "rbi_inflation_target":    "4% (with ±2% tolerance band)",
            "rbi_mandate":             "Flexible inflation targeting under MPC",
            "implication_for_returns": (
                f"Real return = Nominal return – Inflation. "
                f"At current inflation of ~{latest_value}%, "
                f"a 12% equity return gives a real return of ~{12 - latest_value:.1f}%."
            ),
        }

    return {
        "country":           country_code,
        "indicator":         "Consumer Price Index (CPI) Inflation",
        "unit":              "% annual",
        "source":            "World Bank",
        "latest_year":       latest_year,
        "latest_value":      f"{latest_value}%",
        "5_year_average":    f"{avg_5y}%" if avg_5y else "N/A",
        "trend":             trend,
        "annual_series":     {k: f"{v}%" for k, v in series.items()},
        **rbi_context,
        "note": "World Bank data typically has a 1–2 year lag. For real-time India data, check mospi.gov.in.",
    }


# ─────────────────────────────────────────────
# GDP Growth
# ─────────────────────────────────────────────

def get_gdp_growth(country_code: str = "IN") -> Dict[str, Any]:
    """
    Fetch GDP growth rate data from the World Bank API.

    Parameters
    ----------
    country_code : ISO 3166-1 alpha-2 country code (default 'IN' for India).

    Returns
    -------
    Dict with 5-year GDP growth series, GDP size, and economic context.
    """
    raw_growth   = _wb_fetch(WB_INDICATORS["GDP_GROWTH"],      country=country_code, years=DEFAULT_YEARS)
    raw_gdp_usd  = _wb_fetch(WB_INDICATORS["GDP_CURRENT_USD"], country=country_code, years=1)
    raw_per_cap  = _wb_fetch(WB_INDICATORS["GDP_PER_CAPITA"],  country=country_code, years=1)

    if raw_growth is None:
        return {
            "error":   "Could not fetch GDP data from World Bank API.",
            "country": country_code,
            "fallback_info": {
                "India_FY2024_estimated": "~8.2% (IMF estimate)",
                "India_FY2023": "~7.2%",
                "India_FY2022": "~8.7%",
                "source": "IMF World Economic Outlook — World Bank data has a lag",
            },
        }

    growth_series = _format_wb_series(raw_growth)
    if not growth_series:
        return {"error": "No GDP growth data available.", "country": country_code}

    values       = list(growth_series.values())
    latest_year  = list(growth_series.keys())[0]
    latest_value = values[0]
    avg_5y       = round(sum(values) / len(values), 2) if values else None

    # GDP size
    gdp_usd = None
    if raw_gdp_usd:
        for entry in raw_gdp_usd:
            if entry.get("value"):
                gdp_usd = entry["value"]
                break
    gdp_tn_usd = round(gdp_usd / 1e12, 2) if gdp_usd else None

    # Per capita
    per_capita = None
    if raw_per_cap:
        for entry in raw_per_cap:
            if entry.get("value"):
                per_capita = round(entry["value"], 0)
                break

    context = {}
    if country_code.upper() == "IN":
        context = {
            "india_ranking":   "5th largest economy globally (2024, ~$3.7T GDP)",
            "growth_driver":   "Strong domestic consumption, services sector, and capex",
            "implication":     (
                "Higher GDP growth → corporate earnings growth → equity market upside. "
                f"India's {latest_value}% growth is among the fastest globally."
            ),
        }

    return {
        "country":          country_code,
        "indicator":        "GDP Growth Rate",
        "unit":             "% annual (constant prices)",
        "source":           "World Bank",
        "latest_year":      latest_year,
        "latest_value":     f"{latest_value}%",
        "5_year_average":   f"{avg_5y}%" if avg_5y else "N/A",
        "annual_series":    {k: f"{v}%" for k, v in growth_series.items()},
        "gdp_size_trillion_usd": gdp_tn_usd,
        "gdp_per_capita_usd": per_capita,
        **context,
        "note": "World Bank data has a 1–2 year lag. Latest projections from IMF/RBI may differ.",
    }
