# 🇮🇳 FINAI — AI Financial Advisor Agent for India

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://ai-financial-advisor-udqp.onrender.com)

**A production-quality, agentic AI financial advisor purpose-built for India.**  
Real stock prices. Real mutual fund NAVs. Real tax calculations. Zero hallucination.

[🚀 Live Demo](https://ai-financial-advisor-udqp.onrender.com) · [📖 Docs](#table-of-contents) · [🐛 Issues](https://github.com/muditkapoor07/Ai-Financial-Advisor/issues) · [⭐ Star this repo](https://github.com/muditkapoor07/Ai-Financial-Advisor)

</div>

---

## 📸 Screenshot

```
╔══════════════════════════════════════════════════════════════════════════════╗
║          FINAI -- AI Financial Advisor for India                             ║
║   Expertise: CA  CFP  Investment Analyst  Tax Consultant                     ║
║   Coverage:  Stocks  Mutual Funds  Tax  Retirement  Insurance                ║
║   Powered by: Groq (llama-3.3-70b-versatile)                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

You: I'm 30, earn ₹18L/year, want to retire at 55. Build me a full plan.

  🔧 Calling get_inflation_rate()
  ✅ Got result (inflation_rate=5.65...)
  🔧 Calling check_emergency_fund(monthly_expenses=60000, current_savings=...)
  ✅ Got result (status=ADEQUATE...)
  🔧 Calling calculate_retirement_corpus(monthly_expenses=60000, years_to_retirement=25...)
  ✅ Got result (corpus_needed=18429032...)
  🔧 Calling calculate_sip_needed(target_corpus=18429032, annual_return_rate=0.12, years=25)
  ✅ Got result (monthly_sip=9847...)
  🔧 Calling compare_tax_regimes(annual_income=1800000, deductions=...)
  ✅ Got result (recommended=old_regime, savings=42500...)
  🔧 Calling suggest_tax_savings(annual_income=1800000...)
  ✅ Got result (potential_savings=87500...)

╭─────────────────── FINAI — Financial Advisor ───────────────────╮
│                                                                  │
│  ## 📋 Your 25-Year Retirement Master Plan                       │
│  ...                                                             │
╰──────────────────────────────────────────────────────────────────╯
```

---

## Table of Contents

- [✨ What Makes It Truly Agentic](#-what-makes-it-truly-agentic)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🔧 The 22 Tools](#-the-22-tools)
- [🚀 Quickstart](#-quickstart)
- [🌐 Web Interface](#-web-interface)
- [💻 Terminal (CLI) Interface](#-terminal-cli-interface)
- [🔄 Agent Loop Architecture](#-agent-loop-architecture)
- [💬 Example Queries](#-example-queries)
- [📊 Example Output: Full Retirement Plan](#-example-output-full-retirement-plan)
- [🌍 Deployment on Render](#-deployment-on-render)
- [⚙️ Configuration](#️-configuration)
- [🧪 Development](#-development)
- [📚 API Reference](#-api-reference)
- [🤝 Contributing](#-contributing)
- [⚠️ Disclaimer](#️-disclaimer)

---

## ✨ What Makes It Truly Agentic

FINAI is not a chatbot wrapper. It is a **multi-step reasoning agent** that autonomously decides which tools to invoke, executes them against live external APIs, synthesises the results, and produces a final structured response — all without any human guidance mid-turn.

| Property | Description |
|---|---|
| 🧠 **Multi-step reasoning** | Doesn't answer in one shot. Calls multiple tools in sequence, synthesises results, then responds. |
| 📡 **Live data, zero hallucination** | Fetches real-time prices from NSE/BSE (yfinance), live mutual fund NAVs (mfapi.in + AMFI), and macro data (World Bank API). Never fabricates a number. |
| 🤖 **Autonomous tool selection** | The LLM autonomously decides which of 22 tools to call based on the query — no rules or if-else branching. |
| 🔁 **Context memory** | Full conversation history is maintained per session. Follow-up questions work naturally. |
| ⛓️ **Iterative refinement** | Can chain tool calls — e.g. fetch live inflation rate, then feed it into retirement corpus calculation. |
| 🇮🇳 **India-first** | NSE/BSE tickers, ₹ currency, SEBI regulations, FY 2024-25 tax slabs (old + new regime), 80C/80D/HRA/NPS deductions, AMFI mutual fund codes — all built in. |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | [Groq API](https://groq.com) · `llama-3.3-70b-versatile` · function calling |
| **Web server** | [FastAPI](https://fastapi.tiangolo.com) + WebSockets (real-time streaming) |
| **Stock data** | [yfinance](https://github.com/ranaroussi/yfinance) · NSE (`.NS`) and BSE (`.BO`) |
| **Mutual funds** | [mfapi.in](https://www.mfapi.in) + [AMFI](https://www.amfiindia.com) NAV data |
| **Macro data** | [World Bank API](https://datahelpdesk.worldbank.org) · India CPI, GDP |
| **Terminal UI** | [rich](https://github.com/Textualize/rich) · panels, markdown, spinners |
| **Runtime** | Python 3.11.9 |
| **Hosting** | [Render](https://render.com) |

---

## 📁 Project Structure

```
AI Financial Advisor Agent/
│
├── agent.py                  # CLI agent loop — terminal interface, rich UI
├── app.py                    # FastAPI web server + WebSocket handler
│
├── static/
│   └── index.html            # Animated dark-theme chat UI (single-file SPA)
│
├── tools/
│   ├── stock_data.py         # yfinance: NSE/BSE real-time & historical data
│   ├── mutual_fund.py        # mfapi.in: mutual fund NAV + AMFI scheme search
│   ├── economic_data.py      # World Bank: India inflation (CPI) + GDP growth
│   └── financial_health.py  # Emergency fund, DTI, savings rate, HLV insurance
│
├── calculators/
│   ├── sip_calculator.py     # SIP, lumpsum, EMI, retirement corpus, SWP
│   └── tax_calculator.py     # FY 2024-25 old/new regime, 80C/80D/HRA/NPS
│
├── data/
│   └── tax_data.py           # Static FY 2024-25 tax constants (slabs, limits)
│
├── requirements.txt
├── runtime.txt               # python-3.11.9
└── .env.example
```

---

## 🔧 The 22 Tools

FINAI registers 22 tools with the LLM in OpenAI/Groq function-calling format. The model autonomously decides which to call.

### 📈 Stock Data (3 tools)

| Tool | Description |
|---|---|
| `get_stock_price` | Current price, day change, 52-week high/low, P/E, market cap for any NSE (`.NS`) or BSE (`.BO`) stock |
| `get_stock_history` | Historical OHLCV, total return, CAGR, volatility, max drawdown over 1d → max |
| `get_multiple_stocks` | Batch fetch current metrics for a list of symbols simultaneously |

### 💰 Mutual Funds (3 tools)

| Tool | Description |
|---|---|
| `get_fund_nav` | Current NAV, scheme name, fund house for any AMFI scheme code |
| `search_funds` | Search funds by name/keyword to discover AMFI scheme codes |
| `get_fund_details` | Full details: historical NAV, 1W / 1M / 1Y / 3Y / 5Y returns |

### 🌍 Economic Data (2 tools)

| Tool | Description |
|---|---|
| `get_inflation_rate` | India CPI inflation rate — 5-year series from World Bank |
| `get_gdp_growth` | India GDP growth rate — 5-year series from World Bank |

### 🏥 Financial Health (4 tools)

| Tool | Description |
|---|---|
| `check_emergency_fund` | Validates adequacy vs. the 6-month-expenses rule |
| `analyze_debt_burden` | Debt-to-income (DTI) ratio analysis with advice |
| `calculate_savings_rate` | Monthly savings rate + projected wealth at 5Y / 10Y / 20Y horizons |
| `insurance_adequacy_check` | Life cover adequacy using the Human Life Value (HLV) method |

### 🧮 Investment Calculators (6 tools)

| Tool | Description |
|---|---|
| `calculate_sip` | Future value of a SIP with full formula breakdown |
| `calculate_sip_needed` | Reverse SIP: monthly amount needed to reach a target corpus |
| `calculate_lumpsum` | Future value of a one-time lumpsum investment |
| `calculate_emi` | EMI, total interest, and amortisation summary for any loan |
| `calculate_retirement_corpus` | Corpus needed at retirement + monthly SIP required (inflation-adjusted) |
| `calculate_swp` | How long a corpus will last under a Systematic Withdrawal Plan |

### 💼 Tax Planning (4 tools)

| Tool | Description |
|---|---|
| `calculate_tax_old_regime` | FY 2024-25 tax under old regime with all deductions (80C, 80D, HRA, NPS, 24B…) |
| `calculate_tax_new_regime` | FY 2024-25 tax under the new (default) regime |
| `compare_tax_regimes` | Side-by-side comparison with a clear recommendation |
| `suggest_tax_savings` | Analyses current investments and recommends specific actions to reduce tax |

---

## 🚀 Quickstart

### Prerequisites

- Python 3.11+
- A free [Groq API key](https://console.groq.com) (takes ~60 seconds to get)

### 1. Clone the repo

```bash
git clone https://github.com/muditkapoor07/Ai-Financial-Advisor.git
cd Ai-Financial-Advisor
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

`.env` contents:

```env
GROQ_API_KEY=gsk_your_key_here
# MODEL=llama-3.3-70b-versatile   # optional override
```

### 5. Run!

**Web interface (recommended):**

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

**Terminal / CLI:**

```bash
python agent.py
```

---

## 🌐 Web Interface

The web interface is a single-file SPA (`static/index.html`) with:

- 🌑 Animated dark theme
- 💬 Real-time WebSocket chat
- 🔧 Live tool-call indicators (shows which tools are being called as it thinks)
- 📝 Markdown rendering for tables, headers, and code blocks
- 📱 Mobile-responsive layout

The FastAPI server exposes two endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Serves `static/index.html` |
| `/ws` | `WebSocket` | Real-time agent turns, per-session history |

**WebSocket message protocol:**

```json
// Client → Server
"I'm 30, earn ₹18L/year, want to retire at 55."

// Server → Client (event stream)
{"type": "tool_call",   "name": "get_inflation_rate", "input": {}}
{"type": "tool_result", "name": "get_inflation_rate", "ok": true}
{"type": "tool_call",   "name": "calculate_retirement_corpus", "input": {...}}
{"type": "tool_result", "name": "calculate_retirement_corpus", "ok": true}
{"type": "response",    "text": "## 📋 Your 25-Year Retirement Plan\n..."}

// On error
{"type": "error", "message": "Agent error: ..."}
```

---

## 💻 Terminal (CLI) Interface

`agent.py` provides a rich, full-featured terminal experience powered by the `rich` library.

```bash
python agent.py
```

**Terminal commands:**

| Command | Action |
|---|---|
| `help` or `?` | Show categorised example queries |
| `clear` | Clear conversation history (start fresh) |
| `exit` / `quit` / `q` | End the session |

**What you see during a turn:**

```
────────────────────────────────────────────────────────
You: Calculate SIP for ₹2 crore goal in 15 years

  ⠋ FINAI is thinking...
  🔧 Calling calculate_sip_needed(target_corpus=20000000, annual_return_rate=0.12, years=15)
  ✅ Got result (monthly_sip=41239, total_invested=7423020...)

╭──────────────────── FINAI — Financial Advisor ─────────────────────╮
│                                                                     │
│  ## 🧮 SIP Calculation for ₹2 Crore Goal                           │
│  ...                                                                │
╰─────────────────────────────────────────────────────────────────────╯
```

---

## 🔄 Agent Loop Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FINAI Agent Loop                             │
└──────────────────────────────────────────────────────────────────────┘

  User Input (WebSocket / Terminal)
         │
         ▼
  ┌─────────────────────────────────────────────────────────┐
  │  Build Messages Array                                    │
  │  [ system_prompt ] + [ conversation_history ] + [ user ]│
  └─────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────┐
  │  Groq API  ── llama-3.3-70b-versatile                   │
  │  • Receives: messages + 22 tool definitions             │
  │  • Decides: call tools OR produce final response        │
  └─────────────────────────────────────────────────────────┘
         │
    ┌────┴─────────────────────┐
    │                          │
    ▼  finish_reason=tool_calls ▼  finish_reason=stop
  ┌──────────────────┐    ┌──────────────────────────┐
  │  Execute Tools   │    │  Stream Final Response   │
  │  (real APIs)     │    │  back to client          │
  └──────────────────┘    └──────────────────────────┘
    │   yfinance (NSE/BSE)
    │   mfapi.in + AMFI
    │   World Bank API
    │   Local calculators
    │
    ▼  Append tool results to messages
  ┌─────────────────────────────────────────────────────────┐
  │  Loop back to Groq API  (may call more tools)           │
  └─────────────────────────────────────────────────────────┘
```

**Step by step:**

1. User sends a message via WebSocket (web) or terminal (CLI)
2. Groq LLM receives the message + system prompt + all 22 tool definitions
3. LLM decides which tools to call (function calling)
4. Tools execute and return real data (stock prices, NAVs, calculations)
5. Tool results are appended to the message history and fed back to the LLM
6. The LLM generates its final markdown response (or calls more tools)
7. Response is streamed back to the browser / terminal
8. Conversation history is maintained for the entire session

**System prompt configures the agent as a multi-specialist:**

> "You are FINAI, an AI Financial Advisor for India with expertise as a CA, CFP, Investment Analyst, and Tax Consultant."

The agent follows a structured process: **Profile → Health Check → Goal Planning → Investment Strategy → Tax Optimisation → Risk Analysis**.

---

## 💬 Example Queries

### 📊 Stock & Market Data

```
What is the current price of Reliance Industries?
Show me TCS stock performance for the last 1 year
Compare HDFC Bank, ICICI Bank, and Kotak Bank stocks
What is NIFTY 50 doing today?
```

### 💰 Mutual Funds

```
Search for Nifty 50 index funds
What is the NAV of Axis Bluechip Fund?
Show me Mirae Asset Emerging Bluechip fund details and returns
Which large-cap fund has the best 5-year returns?
```

### 🧮 Financial Calculators

```
If I invest ₹10,000/month for 20 years at 12%, how much will I get?
I want ₹2 crore in 15 years. How much SIP do I need?
Calculate EMI for a ₹50 lakh home loan at 8.5% for 20 years
How much should I save for retirement? I'm 30, spend ₹60,000/month
I have ₹1 crore. Can I withdraw ₹50,000/month? How long will it last?
```

### 💼 Tax Planning

```
Calculate my tax for salary of ₹15 lakhs
Should I choose old or new tax regime? My 80C is ₹1.5L, 80D is ₹25K
Compare old vs new tax regime for ₹20L income with 80C of ₹1.5L
How can I save maximum tax on ₹20 lakh income?
```

### 🏥 Financial Health Check

```
Is my emergency fund of ₹2 lakhs enough? Monthly expenses ₹40,000
I earn ₹1 lakh, pay ₹35,000 EMI. Is this healthy?
How much life insurance do I need? Income ₹12L, 2 dependents
What is my savings rate? I earn ₹80K and save ₹20K/month
```

### 🌏 Economy & Macro

```
What is India's current inflation rate?
How fast is India's economy growing?
```

### 📋 Full Financial Reviews

```
I'm 32, earn ₹18L, married with 1 child. Help me plan my finances.
I'm 30, earn ₹18L/year, want to retire at 55. Build me a full plan.
Review my portfolio: 80% equity, 20% FD. Is it right for me?
```

---

## 📊 Example Output: Full Retirement Plan

> **Query:** *"I'm 30, earn ₹18L/year, want to retire at 55. Build me a full plan."*

FINAI calls 6 tools in sequence — inflation rate → emergency fund check → retirement corpus → SIP needed → tax comparison → tax savings — then synthesises:

---

## 📋 Your 25-Year Retirement Master Plan

### 👤 Profile Summary

| Parameter | Value |
|---|---|
| Age | 30 years |
| Annual Income | ₹18,00,000 |
| Monthly Take-Home (est.) | ₹1,26,000 |
| Retirement Age | 55 |
| Years to Retire | **25 years** |
| Expected Retirement Years | 30 years (until age 85) |

---

### 🏥 Step 1: Financial Health Foundation

**Emergency Fund:** Your target is **₹3,60,000** (6× ₹60,000/month expenses).
- Status: Build this first before investing. Park it in a liquid mutual fund (e.g. Nippon India Liquid Fund).

**Life Insurance (HLV Method):**
- Recommended cover: ₹1,80,00,000 (10× annual income)
- Buy a pure **term plan** — ₹1.8 crore cover costs ~₹14,000/year at age 30.

**Health Insurance:**
- Minimum ₹10 lakh individual / ₹15 lakh family floater.

---

### 💰 Step 2: Retirement Corpus Calculation

Using **India CPI inflation: 5.65%** (World Bank, live data)

```
Current monthly expenses       : ₹60,000
Inflation-adjusted at age 55   : ₹60,000 × (1.06)²⁵ = ₹2,57,398/month
Annual expenses in retirement  : ₹30,88,776/year

Corpus required (SWP @ 8% for 30 years):
  C = A × [1 − (1+r)⁻ⁿ] / r
  C = ₹30,88,776 × [1 − (1.08)⁻³⁰] / 0.08
  C = ₹34,76,14,000  ≈  ₹3.48 crore
```

> **Target Corpus at Age 55: ₹3.48 crore**

---

### 📈 Step 3: Investment Strategy

**Monthly SIP Required to Reach ₹3.48 Crore in 25 Years @ 12% p.a.:**

```
  SIP = FV × r / [(1+r)ⁿ − 1]
  SIP = 3,48,00,000 × 0.01 / [(1.01)³⁰⁰ − 1]
  SIP = ₹18,547/month
```

**Recommended Portfolio Allocation (Moderate-Aggressive, age 30):**

| Asset Class | Allocation | Monthly SIP | Instrument |
|---|---|---|---|
| Large Cap Equity | 35% | ₹6,491 | Nifty 50 Index Fund |
| Mid Cap Equity | 25% | ₹4,637 | Mirae Asset Midcap |
| Small Cap Equity | 15% | ₹2,782 | Nippon Small Cap |
| Debt / Bonds | 15% | ₹2,782 | ICICI Pru Corporate Bond |
| Gold | 10% | ₹1,855 | Sovereign Gold Bond / Gold ETF |
| **Total** | **100%** | **₹18,547** | |

---

### 💼 Step 4: Tax Optimisation (FY 2024-25)

**Regime Comparison for ₹18L Income:**

| Regime | Taxable Income | Tax Payable | Effective Rate |
|---|---|---|---|
| New Regime | ₹17,25,000 | ₹2,62,500 | 14.6% |
| Old Regime (with deductions) | ₹13,75,000 | ₹1,92,500 | 10.7% |
| **Savings with Old Regime** | | **₹70,000** | |

✅ **Recommendation: Choose the Old Tax Regime** — save ₹70,000/year.

**Deduction Optimisation:**

| Section | Instrument | Max Limit | Your Usage | Gap |
|---|---|---|---|---|
| 80C | ELSS + EPF + PPF | ₹1,50,000 | ₹72,000 | ₹78,000 |
| 80D | Health insurance | ₹25,000 | ₹0 | ₹25,000 |
| 80CCD(1B) | NPS Tier I | ₹50,000 | ₹0 | ₹50,000 |
| 24(b) | Home loan interest | ₹2,00,000 | ₹0 | — |

**Action:** Invest ₹78,000 more in ELSS + contribute ₹50,000 to NPS = additional tax saving of **₹37,440**.

---

### 🗓️ Step 5: 25-Year Milestone Roadmap

| Age | Milestone | Action |
|---|---|---|
| 30 | Foundation | Build emergency fund (₹3.6L), buy term plan, start SIP |
| 35 | Acceleration | Increase SIP by 10% annually (step-up SIP) |
| 40 | Mid-review | Rebalance equity:debt from 75:25 → 65:35 |
| 45 | Pre-retirement | Shift 20% corpus to debt; review insurance |
| 50 | Consolidation | Move 40% to debt; lock in FDs for near-term expenses |
| 55 | **RETIRE** | Corpus target: ₹3.48 crore → Start SWP @ ₹2.57L/month |

---

### ✅ Immediate Action Items

1. **This week:** Buy ₹1.8 crore term plan and ₹10L health insurance
2. **This month:** Open liquid MF account; park ₹3.6L emergency fund
3. **This month:** Start ₹18,547/month SIP across the 5 funds above
4. **Before March 31:** Invest ₹78,000 in ELSS + ₹50,000 in NPS Tier I
5. **Every year:** Step up SIP by 10% as salary grows

> ⚠️ *Projections assume 12% equity returns and 6% inflation. Actual returns will vary. Past performance is not a guarantee. Consult a SEBI-registered investment advisor for personalised advice.*

---

## 🌍 Deployment on Render

The project is deployed and live at **[https://ai-financial-advisor-udqp.onrender.com](https://ai-financial-advisor-udqp.onrender.com)**.

### Deploy your own instance

1. Fork this repo on GitHub

2. Create a new **Web Service** on [Render](https://render.com)

3. Connect your GitHub repo

4. Configure the service:

   | Setting | Value |
   |---|---|
   | **Environment** | Python |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
   | **Instance Type** | Free (or Starter for production) |

5. Add environment variable:

   | Key | Value |
   |---|---|
   | `GROQ_API_KEY` | `gsk_your_key_here` |

6. Deploy — your instance will be live in ~2 minutes.

---

## ⚙️ Configuration

All configuration is via environment variables (`.env` file or Render dashboard):

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | — | Your Groq API key from [console.groq.com](https://console.groq.com) |
| `MODEL` | ❌ No | `llama-3.3-70b-versatile` | Groq model ID to use |
| `DEBUG` | ❌ No | — | Set to any value to enable full tracebacks in the CLI |

### `.env.example`

```env
# Required
GROQ_API_KEY=gsk_your_key_here

# Optional overrides
# MODEL=llama-3.3-70b-versatile
# DEBUG=1
```

---

## 🧪 Development

### Project dependencies

```
yfinance>=0.2.36       # NSE/BSE stock data
requests>=2.31.0       # HTTP client for APIs
pandas>=2.0.0          # Data manipulation
numpy>=1.24.0          # Numerical calculations
rich>=13.0.0           # Terminal UI
groq>=0.9.0            # Groq API client
python-dotenv>=1.0.0   # .env file loading
fastapi>=0.111.0       # Web framework
uvicorn[standard]>=0.30.0  # ASGI server
```

### Running in development mode

```bash
# Web server with hot reload
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# CLI agent
python agent.py

# Enable debug tracebacks
DEBUG=1 python agent.py
```

### Adding a new tool

1. Implement the function in the appropriate module under `tools/` or `calculators/`

2. Add the tool definition (OpenAI function-calling JSON schema) to the `TOOLS` list in `agent.py`:

```python
{
    "type": "function",
    "function": {
        "name": "my_new_tool",
        "description": "What this tool does and when to use it.",
        "parameters": {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string",
                    "description": "What this parameter is"
                }
            },
            "required": ["param_name"],
        },
    },
}
```

3. Register the function in the `TOOL_MAP` dict in `agent.py`:

```python
TOOL_MAP = {
    ...
    "my_new_tool": my_module.my_new_tool,
}
```

That's it — the LLM will automatically learn to call the new tool from its description.

---

## 📚 API Reference

### WebSocket Protocol

**Endpoint:** `ws://localhost:8000/ws`

**Client → Server:** Plain text (the user's message)

**Server → Client:** JSON events

```typescript
// Tool is being called
{ "type": "tool_call",   "name": string, "input": object }

// Tool completed
{ "type": "tool_result", "name": string, "ok": boolean }

// Final LLM response (markdown)
{ "type": "response",    "text": string }

// Error
{ "type": "error",       "message": string }
```

### REST Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the chat UI (`static/index.html`) |
| `GET` | `/static/*` | Static file assets |
| `WebSocket` | `/ws` | Real-time agent turns |

---

## 🤝 Contributing

Contributions are welcome! Here are some good first areas:

- 📊 Add more stock exchanges (e.g. commodity markets via MCX)
- 🏦 Add fixed deposit / PPF / NPS calculators
- 📅 Add step-up (increasing) SIP support
- 🌐 Add support for multi-language responses (Hindi, Tamil, etc.)
- 🧪 Add unit tests for calculators
- 📱 Improve mobile UI in `static/index.html`

**To contribute:**

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-new-tool`
3. Commit your changes: `git commit -m 'Add MCX commodity price tool'`
4. Push to your fork: `git push origin feature/my-new-tool`
5. Open a Pull Request

---

## ⭐ Star History

If FINAI saved you time or helped you think through a financial decision, please give it a ⭐ — it helps others discover the project!

[![Star History Chart](https://api.star-history.com/svg?repos=muditkapoor07/Ai-Financial-Advisor&type=Date)](https://github.com/muditkapoor07/Ai-Financial-Advisor)

---

## ⚠️ Disclaimer

> FINAI is an AI-powered tool for **educational and informational purposes only**.
>
> - It is **not** a SEBI-registered investment advisor.
> - All financial projections use assumed return rates (equity 12%, debt 7%, gold 8%). **Actual market returns will vary.**
> - Tax calculations are based on FY 2024-25 rules and may not reflect future budget changes.
> - **Always consult a qualified financial advisor (CFP/CA/RIA)** before making investment, tax, or insurance decisions.
> - Past performance of any instrument does not guarantee future results.
> - Mutual fund investments are subject to market risks. Please read all scheme-related documents carefully.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ for India's financial future

[🚀 Try Live Demo](https://ai-financial-advisor-udqp.onrender.com) · [⭐ Star on GitHub](https://github.com/muditkapoor07/Ai-Financial-Advisor) · [🐛 Report a Bug](https://github.com/muditkapoor07/Ai-Financial-Advisor/issues)

</div>
