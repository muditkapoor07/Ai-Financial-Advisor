"""
SIP, Lumpsum, EMI, Retirement and SWP calculators.
All monetary values are in Indian Rupees (₹).
"""

import math
from typing import Dict, Any


# ─────────────────────────────────────────────
# SIP — Systematic Investment Plan
# ─────────────────────────────────────────────

def calculate_sip(
    monthly_investment: float,
    annual_return_rate: float,
    years: int,
) -> Dict[str, Any]:
    """
    Calculate the future value of a SIP (Systematic Investment Plan).

    Formula:
        FV = P × [(1 + r)^n – 1] / r × (1 + r)
    where:
        P = monthly investment
        r = monthly return rate  = annual_return_rate / 12
        n = number of months     = years × 12

    Parameters
    ----------
    monthly_investment   : Monthly SIP amount in ₹
    annual_return_rate   : Expected annualised return (e.g., 0.12 for 12%)
    years                : Investment horizon in years

    Returns
    -------
    dict with future_value, total_invested, total_returns, return_percentage
    """
    r = annual_return_rate / 12          # monthly rate
    n = years * 12                       # total months

    if r == 0:
        future_value = monthly_investment * n
    else:
        future_value = monthly_investment * ((((1 + r) ** n) - 1) / r) * (1 + r)

    total_invested = monthly_investment * n
    total_returns  = future_value - total_invested

    return {
        "monthly_investment":  round(monthly_investment, 2),
        "annual_return_rate":  f"{annual_return_rate * 100:.2f}%",
        "years":               years,
        "total_months":        n,
        "total_invested":      round(total_invested, 2),
        "future_value":        round(future_value, 2),
        "total_returns":       round(total_returns, 2),
        "return_percentage":   round((total_returns / total_invested) * 100, 2),
        "formula": "FV = P × [(1+r)^n – 1] / r × (1+r)  where r = annual_rate/12, n = months",
        "wealth_ratio":        round(future_value / total_invested, 2),
    }


def calculate_sip_needed(
    target_corpus: float,
    annual_return_rate: float,
    years: int,
) -> Dict[str, Any]:
    """
    Reverse SIP: calculate the monthly SIP required to reach a target corpus.

    Derived from FV formula:
        P = FV × r / [(1 + r)^n – 1] / (1 + r)

    Parameters
    ----------
    target_corpus        : Desired future value in ₹
    annual_return_rate   : Expected annualised return (e.g., 0.12 for 12%)
    years                : Investment horizon in years
    """
    r = annual_return_rate / 12
    n = years * 12

    if r == 0:
        monthly_sip = target_corpus / n
    else:
        monthly_sip = target_corpus * r / (((1 + r) ** n - 1) * (1 + r))

    total_invested = monthly_sip * n
    total_returns  = target_corpus - total_invested

    return {
        "target_corpus":       round(target_corpus, 2),
        "monthly_sip_needed":  round(monthly_sip, 2),
        "annual_return_rate":  f"{annual_return_rate * 100:.2f}%",
        "years":               years,
        "total_months":        n,
        "total_invested":      round(total_invested, 2),
        "total_returns":       round(total_returns, 2),
        "formula": "P = FV × r / [(1+r)^n – 1] / (1+r)  where r = annual_rate/12, n = months",
    }


# ─────────────────────────────────────────────
# Lumpsum compounding
# ─────────────────────────────────────────────

def calculate_lumpsum(
    principal: float,
    annual_return_rate: float,
    years: int,
) -> Dict[str, Any]:
    """
    Calculate the future value of a one-time lumpsum investment.

    Formula:  FV = P × (1 + r)^n
    where r = annual return rate,  n = years

    Parameters
    ----------
    principal            : One-time investment amount in ₹
    annual_return_rate   : Expected annualised return
    years                : Investment horizon in years
    """
    future_value    = principal * ((1 + annual_return_rate) ** years)
    total_returns   = future_value - principal
    cagr            = annual_return_rate  # same as input for lumpsum

    return {
        "principal":           round(principal, 2),
        "annual_return_rate":  f"{annual_return_rate * 100:.2f}%",
        "years":               years,
        "future_value":        round(future_value, 2),
        "total_returns":       round(total_returns, 2),
        "return_percentage":   round((total_returns / principal) * 100, 2),
        "wealth_ratio":        round(future_value / principal, 2),
        "formula":             "FV = P × (1 + r)^n",
    }


# ─────────────────────────────────────────────
# EMI — Equated Monthly Instalment
# ─────────────────────────────────────────────

def calculate_emi(
    principal: float,
    annual_rate: float,
    tenure_months: int,
) -> Dict[str, Any]:
    """
    Calculate the EMI, total interest, and amortisation summary for a loan.

    Formula:  EMI = P × r × (1+r)^n / [(1+r)^n – 1]
    where:
        P = principal
        r = monthly interest rate = annual_rate / 12
        n = tenure in months

    Parameters
    ----------
    principal        : Loan amount in ₹
    annual_rate      : Annual interest rate (e.g., 0.085 for 8.5%)
    tenure_months    : Loan tenure in months
    """
    r = annual_rate / 12
    n = tenure_months

    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)

    total_payment    = emi * n
    total_interest   = total_payment - principal
    interest_percent = (total_interest / principal) * 100

    return {
        "loan_amount":         round(principal, 2),
        "annual_interest_rate": f"{annual_rate * 100:.2f}%",
        "tenure_months":       n,
        "tenure_years":        round(n / 12, 1),
        "monthly_emi":         round(emi, 2),
        "total_payment":       round(total_payment, 2),
        "total_interest":      round(total_interest, 2),
        "interest_percentage": round(interest_percent, 2),
        "formula": "EMI = P × r × (1+r)^n / [(1+r)^n – 1]  where r = annual_rate/12",
    }


# ─────────────────────────────────────────────
# Retirement corpus planning
# ─────────────────────────────────────────────

def calculate_retirement_corpus(
    monthly_expenses: float,
    years_to_retirement: int,
    years_in_retirement: int,
    inflation_rate: float = 0.06,
    return_rate: float = 0.08,
) -> Dict[str, Any]:
    """
    Comprehensive retirement corpus calculator.

    Steps:
    1. Inflate current monthly expenses to retirement day
       (monthly_expenses_at_retirement = monthly_expenses × (1+inflation)^years_to_retirement)
    2. Calculate corpus needed at retirement using PV of annuity formula:
       Corpus = R × [1 – (1+r_real)^(-n)] / r_real
       where r_real = (1 + nominal_return) / (1 + inflation) – 1
       and R = monthly expenses at retirement, n = months in retirement
    3. Calculate monthly SIP needed to accumulate that corpus.

    Parameters
    ----------
    monthly_expenses       : Current monthly living expenses in ₹
    years_to_retirement    : Years remaining until retirement
    years_in_retirement    : Expected years of post-retirement life
    inflation_rate         : Annual inflation rate (default 6%)
    return_rate            : Expected portfolio return post-retirement (default 8%)
    """
    # Step 1: Inflate monthly expenses
    monthly_at_retirement = monthly_expenses * ((1 + inflation_rate) ** years_to_retirement)
    annual_at_retirement  = monthly_at_retirement * 12

    # Step 2: Real rate of return post-retirement
    real_return_monthly = ((1 + return_rate) / (1 + inflation_rate)) - 1

    # Step 3: PV of annuity (inflation-adjusted withdrawals for n years)
    n_months  = years_in_retirement * 12
    if real_return_monthly == 0:
        corpus_needed = monthly_at_retirement * n_months
    else:
        corpus_needed = monthly_at_retirement * (
            (1 - (1 + real_return_monthly) ** (-n_months)) / real_return_monthly
        )

    # Step 4: SIP needed to accumulate the corpus
    sip_result = calculate_sip_needed(
        target_corpus=corpus_needed,
        annual_return_rate=0.12,  # Assumed pre-retirement equity returns
        years=years_to_retirement,
    )

    # Step 5: Lumpsum alternative
    lumpsum_result = {}
    if years_to_retirement > 0:
        r_pre = 0.12
        lumpsum_needed = corpus_needed / ((1 + r_pre) ** years_to_retirement)
        lumpsum_result = {
            "lumpsum_needed_today": round(lumpsum_needed, 2),
            "assumed_pre_retirement_return": "12%",
        }

    return {
        "current_monthly_expenses": round(monthly_expenses, 2),
        "years_to_retirement":      years_to_retirement,
        "years_in_retirement":      years_in_retirement,
        "inflation_rate":           f"{inflation_rate * 100:.1f}%",
        "post_retirement_return":   f"{return_rate * 100:.1f}%",
        "monthly_expenses_at_retirement": round(monthly_at_retirement, 2),
        "annual_expenses_at_retirement":  round(annual_at_retirement, 2),
        "corpus_needed_at_retirement":    round(corpus_needed, 2),
        "monthly_sip_needed":             round(sip_result["monthly_sip_needed"], 2),
        "sip_assumed_return":             "12% p.a. (pre-retirement equity portfolio)",
        **lumpsum_result,
        "notes": [
            "Corpus assumes inflation-adjusted withdrawals throughout retirement.",
            "Real return = (1 + nominal) / (1 + inflation) – 1",
            "Pre-retirement SIP assumes 12% equity returns.",
            "Add a buffer of 20–30% for healthcare and emergencies.",
        ],
    }


# ─────────────────────────────────────────────
# SWP — Systematic Withdrawal Plan
# ─────────────────────────────────────────────

def calculate_swp(
    corpus: float,
    monthly_withdrawal: float,
    annual_return_rate: float,
) -> Dict[str, Any]:
    """
    Calculate how long a corpus will last under a Systematic Withdrawal Plan (SWP).

    The corpus grows at annual_return_rate while the investor withdraws monthly.
    We find n such that the corpus is not exhausted.

    Formula each month:
        Corpus_new = Corpus × (1 + r) – monthly_withdrawal
    Closed-form number of months:
        n = –ln(1 – Corpus × r / monthly_withdrawal) / ln(1 + r)

    Parameters
    ----------
    corpus               : Starting portfolio value in ₹
    monthly_withdrawal   : Fixed monthly withdrawal in ₹
    annual_return_rate   : Expected annual return on corpus (e.g., 0.08)
    """
    r = annual_return_rate / 12  # monthly rate

    # Monthly return on corpus
    monthly_return_on_corpus = corpus * r

    if monthly_withdrawal <= 0:
        return {"error": "Monthly withdrawal must be positive."}

    if monthly_withdrawal <= monthly_return_on_corpus:
        # Corpus generates more than withdrawal — it lasts forever
        surplus_monthly  = monthly_return_on_corpus - monthly_withdrawal
        annual_growth    = surplus_monthly * 12
        return {
            "corpus":              round(corpus, 2),
            "monthly_withdrawal":  round(monthly_withdrawal, 2),
            "annual_return_rate":  f"{annual_return_rate * 100:.2f}%",
            "duration":            "Indefinite — corpus keeps growing",
            "monthly_return_on_corpus": round(monthly_return_on_corpus, 2),
            "monthly_surplus":     round(surplus_monthly, 2),
            "corpus_after_10_years": round(
                corpus * ((1 + r) ** 120) - monthly_withdrawal * (((1 + r) ** 120 - 1) / r),
                2
            ),
            "note": "Your withdrawal is less than monthly portfolio returns — corpus is sustainable.",
        }

    if r == 0:
        months = math.floor(corpus / monthly_withdrawal)
    else:
        ratio = corpus * r / monthly_withdrawal
        if ratio >= 1:
            months = float('inf')
        else:
            months = math.floor(-math.log(1 - ratio) / math.log(1 + r))

    years_int   = months // 12
    months_rem  = months % 12
    total_withdrawn = monthly_withdrawal * months

    return {
        "corpus":                round(corpus, 2),
        "monthly_withdrawal":    round(monthly_withdrawal, 2),
        "annual_return_rate":    f"{annual_return_rate * 100:.2f}%",
        "duration_months":       months,
        "duration_years":        years_int,
        "duration_months_extra": months_rem,
        "total_withdrawn":       round(total_withdrawn, 2),
        "monthly_return_on_corpus": round(monthly_return_on_corpus, 2),
        "formula": "n = –ln(1 – Corpus×r / W) / ln(1+r)  where r = annual_rate/12, W = monthly withdrawal",
        "note": (
            "To make corpus last longer: increase return rate, reduce withdrawal, "
            "or invest in inflation-beating instruments."
        ),
    }
