"""
Financial health analysis tools.
Covers emergency fund, debt burden, savings rate, and insurance adequacy.
"""

from typing import Dict, Any


# ─────────────────────────────────────────────
# Emergency Fund
# ─────────────────────────────────────────────

def check_emergency_fund(
    monthly_expenses: float,
    current_savings: float,
) -> Dict[str, Any]:
    """
    Assess whether the emergency fund is adequate.

    Best practice: 6 months of expenses in liquid instruments
    (savings account, liquid fund, FD with easy withdrawal).

    Parameters
    ----------
    monthly_expenses : Monthly household expenses in ₹
    current_savings  : Current liquid savings (savings account + liquid MF, etc.)

    Returns
    -------
    Dict with adequacy score, gap, and recommendations.
    """
    min_months    = 3
    ideal_months  = 6
    max_months    = 12

    min_target   = monthly_expenses * min_months
    ideal_target = monthly_expenses * ideal_months
    max_target   = monthly_expenses * max_months

    months_covered = current_savings / monthly_expenses if monthly_expenses > 0 else 0

    if months_covered >= ideal_months:
        status = "Excellent"
        score  = 100
        color  = "green"
        message = f"Your emergency fund covers {months_covered:.1f} months of expenses. Well done!"
    elif months_covered >= min_months:
        status = "Adequate"
        score  = int((months_covered / ideal_months) * 100)
        color  = "yellow"
        message = (
            f"Your emergency fund covers {months_covered:.1f} months. "
            f"Aim to build it up to {ideal_months} months."
        )
    elif months_covered >= 1:
        status = "Insufficient"
        score  = int((months_covered / ideal_months) * 100)
        color  = "orange"
        message = (
            f"Critical: Your emergency fund covers only {months_covered:.1f} months. "
            f"Prioritise building it to at least {min_months} months."
        )
    else:
        status = "Critical — No Emergency Fund"
        score  = 0
        color  = "red"
        message = "You have no emergency fund. This is your highest financial priority right now."

    gap_to_ideal = max(0, ideal_target - current_savings)
    gap_to_min   = max(0, min_target - current_savings)

    monthly_top_up_ideal = gap_to_ideal / 12 if gap_to_ideal > 0 else 0
    monthly_top_up_min   = gap_to_min / 6 if gap_to_min > 0 else 0

    surplus_beyond_max = max(0, current_savings - max_target)

    return {
        "monthly_expenses":       round(monthly_expenses, 2),
        "current_savings":        round(current_savings, 2),
        "months_covered":         round(months_covered, 1),
        "status":                 status,
        "health_score":           score,
        "min_target_3months":     round(min_target, 2),
        "ideal_target_6months":   round(ideal_target, 2),
        "max_suggested_12months": round(max_target, 2),
        "gap_to_ideal":           round(gap_to_ideal, 2),
        "gap_to_minimum":         round(gap_to_min, 2),
        "monthly_topup_to_reach_ideal_in_1year": round(monthly_top_up_ideal, 2),
        "monthly_topup_to_reach_minimum_in_6months": round(monthly_top_up_min, 2),
        "surplus_beyond_12months": round(surplus_beyond_max, 2),
        "message": message,
        "where_to_keep": [
            "Savings bank account (instant access)",
            "Liquid mutual funds (T+1 or same-day redemption)",
            "Sweep-in FD linked to savings account",
        ],
        "avoid": [
            "Equity / ELSS (volatile, 3-year lock-in)",
            "PPF (lock-in)",
            "Real estate (illiquid)",
        ],
        "surplus_tip": (
            f"If you have ₹{round(surplus_beyond_max):,} beyond 12 months, "
            f"invest the surplus in better-yielding instruments (debt MFs, balanced funds)."
            if surplus_beyond_max > 0 else ""
        ),
    }


# ─────────────────────────────────────────────
# Debt Burden
# ─────────────────────────────────────────────

def analyze_debt_burden(
    monthly_income: float,
    monthly_emi: float,
) -> Dict[str, Any]:
    """
    Analyse the debt-to-income (DTI) ratio and assess financial stress.

    Rule of thumb:
        DTI < 30%  → Healthy
        DTI 30–40% → Manageable (watch carefully)
        DTI 40–50% → Stretched — review expenses
        DTI > 50%  → Danger zone — prioritise debt reduction

    Parameters
    ----------
    monthly_income : Net monthly take-home income in ₹
    monthly_emi    : Total monthly EMI obligations (all loans combined)

    Returns
    -------
    Dict with DTI ratio, status, and debt-management advice.
    """
    if monthly_income <= 0:
        return {"error": "Monthly income must be positive."}

    dti_ratio = (monthly_emi / monthly_income) * 100
    disposable = monthly_income - monthly_emi

    if dti_ratio == 0:
        status  = "Debt-Free"
        score   = 100
        message = "Congratulations! You have no EMI obligations. Focus on wealth building."
    elif dti_ratio < 30:
        status  = "Healthy"
        score   = int(100 - dti_ratio * 2)
        message = (
            f"Your DTI of {dti_ratio:.1f}% is healthy. "
            f"You have comfortable headroom to take on more debt if needed (e.g., home loan)."
        )
    elif dti_ratio < 40:
        status  = "Manageable"
        score   = int(100 - dti_ratio * 2)
        message = (
            f"Your DTI of {dti_ratio:.1f}% is manageable but on the higher side. "
            f"Avoid taking on any new loans until existing EMIs reduce."
        )
    elif dti_ratio < 50:
        status  = "Stretched"
        score   = max(20, int(100 - dti_ratio * 2))
        message = (
            f"Warning: DTI of {dti_ratio:.1f}% is stretched. "
            f"Consider prepaying high-interest loans (personal loan, credit card)."
        )
    else:
        status  = "Danger Zone"
        score   = 10
        message = (
            f"Critical: DTI of {dti_ratio:.1f}% is dangerously high. "
            f"Seek debt counselling, explore loan restructuring, and prioritise debt repayment."
        )

    # Ideal EMI for this income
    ideal_emi_30pct = monthly_income * 0.30
    ideal_emi_40pct = monthly_income * 0.40
    emi_to_reduce   = max(0, monthly_emi - ideal_emi_30pct)

    return {
        "monthly_income":     round(monthly_income, 2),
        "total_monthly_emi":  round(monthly_emi, 2),
        "debt_to_income_ratio": f"{dti_ratio:.1f}%",
        "disposable_income":  round(disposable, 2),
        "status":             status,
        "health_score":       score,
        "ideal_max_emi_30pct": round(ideal_emi_30pct, 2),
        "ideal_max_emi_40pct": round(ideal_emi_40pct, 2),
        "emi_to_reduce_for_healthy_dti": round(emi_to_reduce, 2),
        "message":            message,
        "priority_payoff_strategy": [
            "1. Avalanche: Pay off highest-interest loan first (saves most money)",
            "2. Snowball: Pay off smallest loan first (psychological wins)",
            "3. Consider home loan prepayment for large outstanding balances",
        ],
        "prepayment_tip": (
            "Every ₹1L prepayment on a 9% home loan with 20 years remaining "
            "saves ~₹1.5L in interest."
        ),
    }


# ─────────────────────────────────────────────
# Savings Rate
# ─────────────────────────────────────────────

def calculate_savings_rate(
    monthly_income: float,
    monthly_savings: float,
) -> Dict[str, Any]:
    """
    Analyse the savings rate and its impact on wealth building.

    Benchmarks:
        < 10%  → Very low — lifestyle inflation risk
        10–20% → Moderate
        20–30% → Good
        30–50% → Excellent — on track for financial independence
        > 50%  → FIRE (Financial Independence / Retire Early) territory

    Parameters
    ----------
    monthly_income  : Net monthly take-home income in ₹
    monthly_savings : Amount saved/invested per month in ₹

    Returns
    -------
    Dict with savings rate, benchmarks, and long-term wealth projections.
    """
    if monthly_income <= 0:
        return {"error": "Monthly income must be positive."}

    savings_rate = (monthly_savings / monthly_income) * 100
    expenses     = monthly_income - monthly_savings

    if savings_rate < 10:
        status  = "Very Low"
        score   = int(savings_rate * 5)
        message = (
            f"Savings rate of {savings_rate:.1f}% is very low. "
            f"Aim for at least 20%. Track expenses and identify areas to cut."
        )
    elif savings_rate < 20:
        status  = "Moderate"
        score   = int(40 + savings_rate * 2)
        message = (
            f"Savings rate of {savings_rate:.1f}% is moderate. "
            f"Good start — aim to push towards 30%."
        )
    elif savings_rate < 30:
        status  = "Good"
        score   = int(60 + savings_rate)
        message = f"Savings rate of {savings_rate:.1f}% is good. You are building wealth steadily."
    elif savings_rate < 50:
        status  = "Excellent"
        score   = min(95, int(80 + savings_rate * 0.5))
        message = (
            f"Excellent! Savings rate of {savings_rate:.1f}% puts you firmly on the path "
            f"to financial independence."
        )
    else:
        status  = "FIRE Track"
        score   = 100
        message = (
            f"Outstanding! Savings rate of {savings_rate:.1f}% — you are on the FIRE "
            f"(Financial Independence / Retire Early) track."
        )

    # Project corpus at different time horizons (at 12% annualised equity return)
    annual_savings = monthly_savings * 12
    r_monthly      = 0.12 / 12

    projections = {}
    for years in [5, 10, 15, 20, 30]:
        n = years * 12
        fv = monthly_savings * (((1 + r_monthly) ** n - 1) / r_monthly) * (1 + r_monthly)
        projections[f"{years}_years"] = round(fv, 2)

    # FIRE number (25x annual expenses — 4% rule)
    annual_expenses = expenses * 12
    fire_number     = annual_expenses * 25
    fire_sip_result = {}
    if monthly_savings > 0:
        months_to_fire = 0
        corpus = 0
        for m in range(1, 721):  # cap at 60 years
            corpus = corpus * (1 + r_monthly) + monthly_savings
            if corpus >= fire_number:
                months_to_fire = m
                break
        if months_to_fire > 0:
            fire_sip_result = {
                "fire_number_4pct_rule": round(fire_number, 2),
                "years_to_fire": round(months_to_fire / 12, 1),
            }

    # Suggested savings improvements
    target_20 = monthly_income * 0.20
    target_30 = monthly_income * 0.30
    gap_20     = max(0, target_20 - monthly_savings)
    gap_30     = max(0, target_30 - monthly_savings)

    return {
        "monthly_income":          round(monthly_income, 2),
        "monthly_savings":         round(monthly_savings, 2),
        "monthly_expenses":        round(expenses, 2),
        "savings_rate":            f"{savings_rate:.1f}%",
        "status":                  status,
        "health_score":            score,
        "message":                 message,
        "corpus_projections_at_12pct": projections,
        **fire_sip_result,
        "to_reach_20pct_savings": round(gap_20, 2),
        "to_reach_30pct_savings": round(gap_30, 2),
        "rule_of_thumb": "Save at least 20% of income; invest in equity for long-term wealth.",
        "tips": [
            "Automate SIPs on salary credit day to 'pay yourself first'",
            "Increase SIP by 10% every year (SIP step-up) to beat inflation",
            f"Saving ₹{round(gap_20):,} more/month reaches 20% savings rate",
        ],
    }


# ─────────────────────────────────────────────
# Insurance Adequacy
# ─────────────────────────────────────────────

def insurance_adequacy_check(
    annual_income: float,
    current_life_cover: float,
    dependents: int,
) -> Dict[str, Any]:
    """
    Check if life insurance cover is adequate using the Human Life Value (HLV) method.

    HLV Method: Cover should replace the present value of future income for dependents.
    Simple thumb rule: Cover = 10–20× annual income
    HLV formula: Cover = Annual income × Years to retirement × Income replacement factor

    Parameters
    ----------
    annual_income       : Gross annual income in ₹
    current_life_cover  : Total life insurance sum assured in ₹
    dependents          : Number of financial dependents (spouse, children, parents)

    Returns
    -------
    Dict with adequacy status, recommended cover, and premium estimates.
    """
    # --- Method 1: Simple multiplier ---
    multiplier_low   = 10
    multiplier_high  = 20
    if dependents >= 3:
        multiplier_high = 25
    elif dependents == 0:
        multiplier_high = 5

    recommended_min  = annual_income * multiplier_low
    recommended_max  = annual_income * multiplier_high

    # --- Method 2: HLV (simplified) ---
    # Assume: 30 working years remaining, 6% inflation, 8% discount rate
    years_remaining  = 30
    real_rate        = (1.08 / 1.06) - 1  # ~1.89%
    hlv              = annual_income * ((1 - (1 + real_rate) ** (-years_remaining)) / real_rate)
    hlv              = round(hlv)

    # Evaluate current cover
    cover_ratio   = current_life_cover / annual_income if annual_income > 0 else 0
    gap           = max(0, recommended_min - current_life_cover)
    gap_hlv       = max(0, hlv - current_life_cover)

    if current_life_cover >= recommended_max:
        status  = "Well Covered"
        score   = 100
        message = (
            f"Your life cover of ₹{current_life_cover/1e7:.2f} Cr is excellent "
            f"({cover_ratio:.0f}× income)."
        )
    elif current_life_cover >= recommended_min:
        status  = "Adequately Covered"
        score   = 75
        message = (
            f"Cover of ₹{current_life_cover/1e7:.2f} Cr is adequate "
            f"but consider topping up to ₹{recommended_max/1e7:.2f} Cr."
        )
    elif current_life_cover > 0:
        status  = "Under-insured"
        score   = int(current_life_cover / recommended_min * 50)
        message = (
            f"You are under-insured. Current cover of ₹{current_life_cover/1e5:.0f}L "
            f"falls short of the recommended ₹{recommended_min/1e7:.2f} Cr."
        )
    else:
        status  = "No Life Insurance"
        score   = 0
        message = (
            "Critical: No life insurance. With dependents, this is an urgent priority. "
            "A term plan is cheap and provides the highest cover."
        )

    # Term plan premium estimate (rough: ~₹10,000 p.a. per ₹1Cr cover for 35-year-old non-smoker)
    additional_cover_needed = gap
    premium_estimate        = additional_cover_needed * 10_000 / 1e7  # rough ₹10K per 1Cr

    return {
        "annual_income":           round(annual_income, 2),
        "current_life_cover":      round(current_life_cover, 2),
        "dependents":              dependents,
        "cover_to_income_ratio":   f"{cover_ratio:.1f}×",
        "status":                  status,
        "health_score":            score,
        "recommended_min_cover":   round(recommended_min, 2),
        "recommended_max_cover":   round(recommended_max, 2),
        "hlv_recommended_cover":   hlv,
        "shortfall_vs_min":        round(gap, 2),
        "shortfall_vs_hlv":        round(gap_hlv, 2),
        "message":                 message,
        "additional_premium_estimate": f"~₹{round(premium_estimate):,} p.a. for additional cover",
        "term_plan_tips": [
            "Buy a pure term plan (NOT endowment/ULIP) — cheapest and best coverage",
            "Cover duration: till age 60–65 or end of major financial liabilities",
            "Include critical illness and accidental disability riders",
            "Medical exam is needed for high-cover plans — disclose health conditions",
            "Choose insurer with 98%+ claim settlement ratio",
        ],
        "additional_insurance_checklist": [
            f"✅ Health insurance: ₹10L–25L cover per family member",
            f"✅ Personal accident cover: 5–10× annual income",
            f"✅ Critical illness cover: ₹25L–50L (for cancer, heart attack, etc.)",
            f"{'✅' if dependents == 0 else '❌'} If no dependents: life insurance less critical",
        ],
    }
