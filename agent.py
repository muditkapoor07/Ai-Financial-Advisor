"""
AI Financial Advisor Agent
==========================
Production-quality conversational financial advisor for India, built on the
Groq API (llama-3.3-70b-versatile) with function calling for real market data
and financial calculations.

Run:
    python agent.py

Requires:
    GROQ_API_KEY in .env or environment
"""

import os
import sys
import json
import traceback

# Force UTF-8 output on Windows to handle unicode characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Fix SSL certificate verification on corporate/enterprise Windows networks
try:
    import certifi_win32.wrapt_certifi  # noqa: F401
except ImportError:
    pass

from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from dotenv import load_dotenv

# ── Internal modules ──────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import stock_data, mutual_fund, economic_data, financial_health
from calculators import sip_calculator, tax_calculator

# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────

load_dotenv()

console = Console()
client  = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")

# ─────────────────────────────────────────────────────────────────────────────
# System prompt
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are FINAI — an autonomous AI Financial Advisor with expertise equivalent to:
• Chartered Accountant (CA) — India, trained in taxation, auditing, and accounting
• Certified Financial Planner (CFP) — goal-based financial planning
• Investment Analyst — equity research, mutual funds, portfolio construction
• Tax Consultant — Indian tax system, ITR filing, tax optimisation

You serve Indian clients and follow a structured advisory process:

═══════════════════════════════════════════════════
  ADVISORY FRAMEWORK (follow in order)
═══════════════════════════════════════════════════
1. PROFILE BUILDING
   • Age, income, family status, risk appetite (1–10)
   • Current assets (equity, debt, real estate, gold, FDs)
   • Liabilities (home loan, car loan, personal loan)
   • Financial goals (retirement, child education, home, vacation, emergency fund)

2. FINANCIAL HEALTH CHECK
   • Emergency fund adequacy (target: 6 months expenses)
   • Debt-to-income ratio (target: < 30%)
   • Savings rate (target: ≥ 20% of income)
   • Insurance coverage (life, health, term plan)

3. GOAL-BASED PLANNING
   • Assign timeline and corpus to each goal
   • Calculate SIP required for each goal
   • Account for inflation (default 6% unless specified)

4. INVESTMENT STRATEGY
   • Recommend asset allocation (equity/debt/gold/cash) based on risk
   • Suggest specific mutual funds or indices for each bucket
   • Provide current NAV and performance data when asked

5. TAX OPTIMISATION
   • Compare old vs. new regime — recommend the better one
   • Maximise 80C (ELSS > PPF > NPS), 80CCD(1B), 80D
   • HRA, home loan deductions analysis

6. RISK ANALYSIS
   • Identify key financial risks: job loss, medical emergency, market crash
   • Suggest mitigation strategies

═══════════════════════════════════════════════════
  PRINCIPLES
═══════════════════════════════════════════════════
• ALWAYS ask clarifying questions before giving specific advice
• Use tools to fetch REAL market data (never make up stock prices/NAVs)
• Show ALL calculations with formulas — not just results
• Account for inflation in every long-term calculation (default 6%)
• Be conservative and realistic with return assumptions:
  - Equity: 12% p.a. long-term
  - Debt/FD: 7% p.a.
  - PPF: 7.1% p.a.
  - Gold: 8% p.a.
  - Balanced: 10% p.a.
• Recommend DIVERSIFIED portfolios; never put all eggs in one basket
• Disclose: "Past performance is not a guarantee of future returns"
• NEVER recommend specific stocks for speculative purposes
• Give India-specific advice (INR, Indian tax laws, SEBI regulations)
• Format monetary amounts in Indian numbering (lakh / crore)
• Prioritise financial security (emergency fund, insurance) before investments

═══════════════════════════════════════════════════
  RISK PROFILES
═══════════════════════════════════════════════════
Conservative (1–3): 20% equity, 60% debt, 20% gold/cash
Moderate (4–6):     50% equity, 35% debt, 15% gold
Aggressive (7–10):  75% equity, 20% debt, 5% gold

═══════════════════════════════════════════════════
  RESPONSE STYLE
═══════════════════════════════════════════════════
• Use markdown formatting with headers, bullet points, and tables
• Start with a brief summary, then detailed analysis
• End with clear ACTION ITEMS the user can implement today
• Use emojis sparingly to enhance readability (not excessively)
• If data is unavailable or uncertain, say so clearly
"""

# ─────────────────────────────────────────────────────────────────────────────
# Tool definitions (OpenAI/Groq function-calling format)
# ─────────────────────────────────────────────────────────────────────────────

TOOLS = [
    # ── Stock data ────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": (
                "Get the current stock price, day change, 52-week high/low, P/E ratio, "
                "market cap, and other key metrics for an NSE or BSE listed Indian stock. "
                "Use NSE suffix .NS (e.g., RELIANCE.NS, TCS.NS) or BSE suffix .BO."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol. Append .NS for NSE or .BO for BSE. "
                                       "Examples: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.BO",
                    }
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_history",
            "description": (
                "Get historical OHLCV data, total return, CAGR, volatility, and max drawdown "
                "for a stock over a specified period."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., TCS.NS)",
                    },
                    "period": {
                        "type": "string",
                        "description": "Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max",
                        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                    },
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_multiple_stocks",
            "description": "Fetch current prices and key metrics for multiple stocks simultaneously.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock symbols e.g. ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']",
                    }
                },
                "required": ["symbols"],
            },
        },
    },
    # ── Mutual funds ──────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_fund_nav",
            "description": "Fetch the current NAV, scheme name, fund house, and basic details for a mutual fund by AMFI scheme code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scheme_code": {
                        "type": "string",
                        "description": "AMFI scheme code (numeric). Use search_funds to find codes. "
                                       "Example: '120503' for Axis Bluechip Fund.",
                    }
                },
                "required": ["scheme_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_funds",
            "description": "Search for mutual funds by name or keyword to find AMFI scheme codes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term e.g. 'axis bluechip', 'nifty 50 index', 'mirae emerging'",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fund_details",
            "description": "Fetch full mutual fund details including historical NAV, 1-week/1-month/1-year/3-year/5-year returns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scheme_code": {
                        "type": "string",
                        "description": "AMFI scheme code (numeric string)",
                    }
                },
                "required": ["scheme_code"],
            },
        },
    },
    # ── Economic data ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_inflation_rate",
            "description": "Fetch India's CPI inflation rate data from the World Bank API (5-year series).",
            "parameters": {
                "type": "object",
                "properties": {
                    "country_code": {
                        "type": "string",
                        "description": "ISO country code (default 'IN' for India)",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_gdp_growth",
            "description": "Fetch India's GDP growth rate data from the World Bank API (5-year series).",
            "parameters": {
                "type": "object",
                "properties": {
                    "country_code": {
                        "type": "string",
                        "description": "ISO country code (default 'IN' for India)",
                    }
                },
                "required": [],
            },
        },
    },
    # ── Financial health ──────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "check_emergency_fund",
            "description": "Check if the emergency fund is adequate (rule: 6 months of expenses in liquid form).",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_expenses": {
                        "type": "number",
                        "description": "Monthly household expenses in ₹",
                    },
                    "current_savings": {
                        "type": "number",
                        "description": "Current liquid savings (savings account + liquid MF) in ₹",
                    },
                },
                "required": ["monthly_expenses", "current_savings"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_debt_burden",
            "description": "Analyse debt-to-income (DTI) ratio and provide debt management advice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_income": {
                        "type": "number",
                        "description": "Net monthly take-home income in ₹",
                    },
                    "monthly_emi": {
                        "type": "number",
                        "description": "Total monthly EMI obligations (all loans) in ₹",
                    },
                },
                "required": ["monthly_income", "monthly_emi"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_savings_rate",
            "description": "Analyse the monthly savings rate and project future wealth at different time horizons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_income": {
                        "type": "number",
                        "description": "Net monthly take-home income in ₹",
                    },
                    "monthly_savings": {
                        "type": "number",
                        "description": "Amount saved/invested per month in ₹",
                    },
                },
                "required": ["monthly_income", "monthly_savings"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "insurance_adequacy_check",
            "description": "Check if life insurance cover is adequate using the Human Life Value (HLV) method.",
            "parameters": {
                "type": "object",
                "properties": {
                    "annual_income": {
                        "type": "number",
                        "description": "Gross annual income in ₹",
                    },
                    "current_life_cover": {
                        "type": "number",
                        "description": "Total life insurance sum assured in ₹",
                    },
                    "dependents": {
                        "type": "integer",
                        "description": "Number of financial dependents (spouse, children, parents)",
                    },
                },
                "required": ["annual_income", "current_life_cover", "dependents"],
            },
        },
    },
    # ── SIP / Investment calculators ──────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "calculate_sip",
            "description": "Calculate the future value of a SIP (Systematic Investment Plan) with formula.",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_investment": {
                        "type": "number",
                        "description": "Monthly SIP amount in ₹",
                    },
                    "annual_return_rate": {
                        "type": "number",
                        "description": "Expected annual return rate as decimal (e.g., 0.12 for 12%)",
                    },
                    "years": {
                        "type": "integer",
                        "description": "Investment horizon in years",
                    },
                },
                "required": ["monthly_investment", "annual_return_rate", "years"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_sip_needed",
            "description": "Reverse SIP: calculate the monthly SIP needed to reach a target corpus.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_corpus": {
                        "type": "number",
                        "description": "Desired future corpus amount in ₹",
                    },
                    "annual_return_rate": {
                        "type": "number",
                        "description": "Expected annual return rate as decimal (e.g., 0.12 for 12%)",
                    },
                    "years": {
                        "type": "integer",
                        "description": "Time horizon in years",
                    },
                },
                "required": ["target_corpus", "annual_return_rate", "years"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_lumpsum",
            "description": "Calculate the future value of a one-time lumpsum investment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {
                        "type": "number",
                        "description": "One-time investment amount in ₹",
                    },
                    "annual_return_rate": {
                        "type": "number",
                        "description": "Expected annual return rate as decimal",
                    },
                    "years": {
                        "type": "integer",
                        "description": "Investment horizon in years",
                    },
                },
                "required": ["principal", "annual_return_rate", "years"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_emi",
            "description": "Calculate EMI, total interest, and amortisation summary for any loan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {
                        "type": "number",
                        "description": "Loan amount in ₹",
                    },
                    "annual_rate": {
                        "type": "number",
                        "description": "Annual interest rate as decimal (e.g., 0.085 for 8.5%)",
                    },
                    "tenure_months": {
                        "type": "integer",
                        "description": "Loan tenure in months",
                    },
                },
                "required": ["principal", "annual_rate", "tenure_months"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_retirement_corpus",
            "description": (
                "Comprehensive retirement planning: calculates the corpus needed at retirement "
                "and the monthly SIP required to accumulate it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_expenses": {
                        "type": "number",
                        "description": "Current monthly living expenses in ₹",
                    },
                    "years_to_retirement": {
                        "type": "integer",
                        "description": "Years remaining until retirement",
                    },
                    "years_in_retirement": {
                        "type": "integer",
                        "description": "Expected years of post-retirement life (e.g., 25–30)",
                    },
                    "inflation_rate": {
                        "type": "number",
                        "description": "Annual inflation rate as decimal (default 0.06 for 6%)",
                    },
                    "return_rate": {
                        "type": "number",
                        "description": "Post-retirement portfolio return as decimal (default 0.08 for 8%)",
                    },
                },
                "required": ["monthly_expenses", "years_to_retirement", "years_in_retirement"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_swp",
            "description": "Calculate how long a corpus will last under a Systematic Withdrawal Plan (SWP).",
            "parameters": {
                "type": "object",
                "properties": {
                    "corpus": {
                        "type": "number",
                        "description": "Starting portfolio / corpus value in ₹",
                    },
                    "monthly_withdrawal": {
                        "type": "number",
                        "description": "Fixed monthly withdrawal amount in ₹",
                    },
                    "annual_return_rate": {
                        "type": "number",
                        "description": "Expected annual return on corpus as decimal (e.g., 0.08)",
                    },
                },
                "required": ["corpus", "monthly_withdrawal", "annual_return_rate"],
            },
        },
    },
    # ── Tax calculators ───────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "calculate_tax_old_regime",
            "description": "Calculate income tax under the Old Tax Regime for FY 2024-25 with all deductions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "annual_income": {
                        "type": "number",
                        "description": "Gross annual income in ₹",
                    },
                    "deductions": {
                        "type": "object",
                        "description": (
                            "Optional deductions dict. Keys: basic_salary, hra_received, "
                            "actual_rent_paid, city, deduction_80c, deduction_80ccd1b, "
                            "deduction_80d_self, deduction_80d_parents, deduction_24b, "
                            "deduction_80e, deduction_80tta, professional_tax, other_deductions"
                        ),
                    },
                },
                "required": ["annual_income"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_tax_new_regime",
            "description": "Calculate income tax under the New Tax Regime for FY 2024-25 (default regime).",
            "parameters": {
                "type": "object",
                "properties": {
                    "annual_income": {
                        "type": "number",
                        "description": "Gross annual income in ₹",
                    }
                },
                "required": ["annual_income"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_tax_regimes",
            "description": "Compare old and new tax regimes and recommend which one saves more tax.",
            "parameters": {
                "type": "object",
                "properties": {
                    "annual_income": {
                        "type": "number",
                        "description": "Gross annual income in ₹",
                    },
                    "deductions": {
                        "type": "object",
                        "description": "Deductions applicable under old regime (same keys as calculate_tax_old_regime)",
                    },
                },
                "required": ["annual_income"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_80c_investments",
            "description": "Track 80C investments against the ₹1.5L limit and show utilisation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "investments": {
                        "type": "object",
                        "description": "Dict of investment name → amount. E.g. {'EPF': 72000, 'ELSS': 50000, 'PPF': 28000}",
                    }
                },
                "required": ["investments"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_tax_savings",
            "description": "Analyse current investments and suggest how to save more tax with specific actions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "annual_income": {
                        "type": "number",
                        "description": "Gross annual income in ₹",
                    },
                    "current_investments": {
                        "type": "object",
                        "description": "Current investments/deductions dict (same keys as deductions in old regime)",
                    },
                },
                "required": ["annual_income"],
            },
        },
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Tool dispatcher
# ─────────────────────────────────────────────────────────────────────────────

TOOL_MAP = {
    # Stock
    "get_stock_price":       stock_data.get_stock_price,
    "get_stock_history":     stock_data.get_stock_history,
    "get_multiple_stocks":   stock_data.get_multiple_stocks,
    # Mutual funds
    "get_fund_nav":          mutual_fund.get_fund_nav,
    "search_funds":          mutual_fund.search_funds,
    "get_fund_details":      mutual_fund.get_fund_details,
    # Economic
    "get_inflation_rate":    economic_data.get_inflation_rate,
    "get_gdp_growth":        economic_data.get_gdp_growth,
    # Financial health
    "check_emergency_fund":     financial_health.check_emergency_fund,
    "analyze_debt_burden":      financial_health.analyze_debt_burden,
    "calculate_savings_rate":   financial_health.calculate_savings_rate,
    "insurance_adequacy_check": financial_health.insurance_adequacy_check,
    # SIP / investment
    "calculate_sip":               sip_calculator.calculate_sip,
    "calculate_sip_needed":        sip_calculator.calculate_sip_needed,
    "calculate_lumpsum":           sip_calculator.calculate_lumpsum,
    "calculate_emi":               sip_calculator.calculate_emi,
    "calculate_retirement_corpus": sip_calculator.calculate_retirement_corpus,
    "calculate_swp":               sip_calculator.calculate_swp,
    # Tax
    "calculate_tax_old_regime":  tax_calculator.calculate_tax_old_regime,
    "calculate_tax_new_regime":  tax_calculator.calculate_tax_new_regime,
    "compare_tax_regimes":       tax_calculator.compare_tax_regimes,
    "calculate_80c_investments": tax_calculator.calculate_80c_investments,
    "suggest_tax_savings":       tax_calculator.suggest_tax_savings,
}


def _sanitize_params(params: dict) -> dict:
    """Unwrap {type, value} objects that some models emit instead of raw values."""
    cleaned = {}
    for k, v in params.items():
        if isinstance(v, dict) and "value" in v:
            cleaned[k] = v["value"]
        else:
            cleaned[k] = v
    return cleaned


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a JSON string."""
    if tool_name not in TOOL_MAP:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    func = TOOL_MAP[tool_name]
    tool_input = _sanitize_params(tool_input)
    try:
        result = func(**tool_input)
        return json.dumps(result, indent=2, default=str)
    except TypeError as e:
        return json.dumps({"error": f"Invalid tool arguments for '{tool_name}': {str(e)}"})
    except Exception as e:
        return json.dumps({
            "error":     f"Tool '{tool_name}' failed: {str(e)}",
            "traceback": traceback.format_exc(),
        })

# ─────────────────────────────────────────────────────────────────────────────
# UI helpers
# ─────────────────────────────────────────────────────────────────────────────

WELCOME_BANNER = """
+==============================================================================+
|                                                                              |
|          FINAI -- AI Financial Advisor for India                             |
|                                                                              |
|   Expertise: CA  CFP  Investment Analyst  Tax Consultant                     |
|   Coverage:  Stocks  Mutual Funds  Tax  Retirement  Insurance                |
|   Powered by: Groq (llama-3.3-70b-versatile)                                |
|                                                                              |
|   Type your question or say 'help' for example queries.                      |
|   Type 'exit' or 'quit' to end the session.                                 |
|                                                                              |
+==============================================================================+
"""

HELP_TEXT = """
## Example Questions

### 📊 Stock & Market Data
- "What is the current price of Reliance Industries?"
- "Show me TCS stock performance for the last 1 year"
- "Compare HDFC Bank, ICICI Bank, and Kotak Bank stocks"

### 💰 Mutual Funds
- "Search for Nifty 50 index funds"
- "What is the NAV of Axis Bluechip Fund?"
- "Show me Mirae Asset Emerging Bluechip fund details and returns"

### 🧮 Financial Calculators
- "If I invest ₹10,000/month for 20 years at 12%, how much will I get?"
- "I want ₹2 crore in 15 years. How much SIP do I need?"
- "Calculate EMI for a ₹50 lakh home loan at 8.5% for 20 years"
- "How much should I save for retirement? I'm 30, spend ₹60,000/month"
- "I have ₹1 crore. Can I withdraw ₹50,000/month? How long will it last?"

### 💼 Tax Planning
- "Calculate my tax for salary of ₹15 lakhs"
- "Should I choose old or new tax regime? My 80C is ₹1.5L, 80D is ₹25K"
- "How can I save maximum tax on ₹20 lakh income?"
- "Show my 80C investments utilisation"

### 🏥 Financial Health
- "Is my emergency fund of ₹2 lakhs enough? Monthly expenses ₹40,000"
- "I earn ₹1 lakh, pay ₹35,000 EMI. Is this healthy?"
- "How much life insurance do I need? Income ₹12L, 2 dependents"

### 🌏 Economy
- "What is India's current inflation rate?"
- "How fast is India's economy growing?"

### 📋 Full Financial Review
- "I'm 32, earn ₹18L, married with 1 child. Help me plan my finances."
- "Review my portfolio: 80% equity, 20% FD. Is it right for me?"
"""


def print_welcome():
    console.print(WELCOME_BANNER, style="bold cyan")
    console.print()


def print_tool_call(tool_name: str, tool_input: dict):
    input_summary = ", ".join(f"{k}={v}" for k, v in list(tool_input.items())[:3])
    console.print(
        f"  🔧 [dim]Calling[/dim] [yellow]{tool_name}[/yellow]"
        f"[dim]({input_summary})[/dim]"
    )


def print_tool_result_summary(tool_name: str, result_str: str):
    try:
        result = json.loads(result_str)
        if "error" in result:
            console.print(f"  ⚠️  [red]Tool error:[/red] {result['error']}")
        else:
            keys = list(result.keys())[:2]
            summary_parts = []
            for k in keys:
                v = result[k]
                if isinstance(v, (str, int, float)):
                    summary_parts.append(f"{k}={v}")
            summary = ", ".join(summary_parts)
            console.print(f"  ✅ [green]Got result[/green] [dim]({summary}...)[/dim]")
    except Exception:
        console.print(f"  ✅ [green]{tool_name} completed[/green]")


def display_assistant_response(text: str):
    console.print()
    console.print(Rule(style="cyan"))
    console.print(
        Panel(
            Markdown(text),
            title="[bold cyan]FINAI — Financial Advisor[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()


def get_user_input() -> str:
    console.print(Rule(style="dim"))
    try:
        user_input = console.input("[bold green]You:[/bold green] ").strip()
    except (EOFError, KeyboardInterrupt):
        return "exit"
    return user_input

# ─────────────────────────────────────────────────────────────────────────────
# Core agent loop
# ─────────────────────────────────────────────────────────────────────────────

def run_agent_turn(messages: list) -> str:
    """
    Run one turn of the agent loop using Groq's OpenAI-compatible API.

    Sends messages to the model, handles tool_calls by executing them
    and feeding results back, and repeats until the model gives a final response.
    """
    # Prepend system message
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    while True:
        with console.status("[bold yellow]FINAI is thinking...[/bold yellow]", spinner="dots"):
            response = client.chat.completions.create(
                model=MODEL,
                messages=full_messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=8096,
            )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # No tool calls — final response
        if finish_reason == "stop" or not message.tool_calls:
            return message.content or ""

        # Has tool calls
        if message.tool_calls:
            # Append assistant message with tool_calls
            full_messages.append({
                "role":       "assistant",
                "content":    message.content or "",
                "tool_calls": [
                    {
                        "id":       tc.id,
                        "type":     "function",
                        "function": {
                            "name":      tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            # Execute each tool and append results
            for tc in message.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_input = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_input = {}

                print_tool_call(tool_name, tool_input)
                result_str = execute_tool(tool_name, tool_input)
                print_tool_result_summary(tool_name, result_str)

                full_messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      result_str,
                })

            # Loop — model will now produce its final response
            continue

        # Fallback
        return message.content or f"[Unexpected finish_reason: {finish_reason}]"

# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    if not os.getenv("GROQ_API_KEY"):
        console.print(
            Panel(
                "[bold red]GROQ_API_KEY not set![/bold red]\n\n"
                "Add to your [yellow].env[/yellow] file:\n"
                "[green]GROQ_API_KEY=gsk_...[/green]",
                title="Configuration Error",
                border_style="red",
            )
        )
        sys.exit(1)

    print_welcome()

    conversation: list = []

    while True:
        user_input = get_user_input()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye", "q"):
            console.print(
                Panel(
                    "Thank you for using FINAI! 🙏\n\n"
                    "[italic]Remember: Investments are subject to market risks. "
                    "Consult a qualified financial advisor for personalised advice.[/italic]",
                    title="[bold cyan]Goodbye![/bold cyan]",
                    border_style="cyan",
                )
            )
            break

        if user_input.lower() in ("help", "?", "examples"):
            console.print(Markdown(HELP_TEXT))
            continue

        if user_input.lower() == "clear":
            conversation.clear()
            console.print("[dim]Conversation history cleared.[/dim]")
            continue

        conversation.append({"role": "user", "content": user_input})

        try:
            final_response = run_agent_turn(conversation)
            conversation.append({"role": "assistant", "content": final_response})
            display_assistant_response(final_response)

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            if os.getenv("DEBUG"):
                console.print_exception()


if __name__ == "__main__":
    main()
