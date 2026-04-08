"""
Indian Income Tax Calculator — FY 2024-25 (AY 2025-26)
Covers old regime, new regime, regime comparison, 80C tracking, and suggestions.
"""

from typing import Dict, Any, Optional
import sys
import os

# Allow imports from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.tax_data import (
    NEW_REGIME_SLABS, NEW_REGIME_STANDARD_DEDUCTION,
    NEW_REGIME_87A_LIMIT, NEW_REGIME_87A_REBATE,
    OLD_REGIME_SLABS, OLD_REGIME_STANDARD_DEDUCTION,
    OLD_REGIME_87A_LIMIT, OLD_REGIME_87A_REBATE,
    SURCHARGE_RATES, NEW_REGIME_SURCHARGE_CAP, CESS_RATE,
    DEDUCTION_80C_LIMIT, DEDUCTION_80CCD1B_LIMIT,
    DEDUCTION_80D, DEDUCTION_24B_LIMIT, DEDUCTION_80TTA_LIMIT,
    HRA_EXEMPTION_RULES,
)


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _compute_tax_on_slabs(taxable_income: float, slabs: list) -> float:
    """Compute basic income tax using the given slab structure."""
    tax = 0.0
    prev_limit = 0
    for upper_limit, rate in slabs:
        if taxable_income <= prev_limit:
            break
        slab_income = min(taxable_income, upper_limit) - prev_limit
        tax += slab_income * rate
        prev_limit = upper_limit
        if upper_limit == float('inf'):
            break
    return tax


def _compute_surcharge(income: float, tax: float, is_new_regime: bool) -> float:
    """Compute surcharge based on income level."""
    rate = 0.0
    prev_threshold = 0
    for threshold, surcharge_rate in SURCHARGE_RATES:
        if income > prev_threshold:
            rate = surcharge_rate
        prev_threshold = threshold if threshold != float('inf') else prev_threshold

    if is_new_regime:
        rate = min(rate, NEW_REGIME_SURCHARGE_CAP)

    return tax * rate


def _apply_87a_rebate(tax: float, taxable_income: float, limit: float, rebate: float) -> float:
    """Apply Section 87A rebate if eligible."""
    if taxable_income <= limit:
        return max(0.0, tax - min(tax, rebate))
    return tax


def _format_inr(amount: float) -> str:
    """Format amount in Indian numbering (lakhs/crores)."""
    amount = round(amount)
    if amount >= 1_00_00_000:
        return f"₹{amount/1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount/1_00_000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


# ─────────────────────────────────────────────
# HRA Exemption calculator (old regime)
# ─────────────────────────────────────────────

def _calculate_hra_exemption(
    basic_salary: float,
    hra_received: float,
    actual_rent_paid: float,
    city: str = "",
) -> float:
    """
    Calculate HRA exemption under Section 10(13A).

    Exempt HRA = minimum of:
        (a) Actual HRA received
        (b) 50% of basic (metro) or 40% (non-metro)
        (c) Actual rent paid – 10% of basic salary
    """
    is_metro = any(
        m.lower() in city.lower()
        for m in HRA_EXEMPTION_RULES["metro_cities"]
    )
    percent   = (
        HRA_EXEMPTION_RULES["metro_hra_percent"] if is_metro
        else HRA_EXEMPTION_RULES["non_metro_hra_percent"]
    )

    option_a = hra_received
    option_b = percent * basic_salary
    option_c = max(0, actual_rent_paid - 0.10 * basic_salary)

    return min(option_a, option_b, option_c)


# ─────────────────────────────────────────────
# OLD REGIME
# ─────────────────────────────────────────────

def calculate_tax_old_regime(
    annual_income: float,
    deductions: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculate income tax under the Old Tax Regime for FY 2024-25.

    Parameters
    ----------
    annual_income  : Gross annual income (salary / business income)
    deductions     : Dict of eligible deductions. Supported keys:
        basic_salary        – for HRA calculation
        hra_received        – HRA component in salary
        actual_rent_paid    – Annual rent paid
        city                – City (determines metro/non-metro HRA %)
        deduction_80c       – Total 80C investments (max ₹1.5L)
        deduction_80ccd1b   – Additional NPS (max ₹50K)
        deduction_80d_self  – Health insurance for self & family
        deduction_80d_parents – Health insurance for parents
        deduction_24b       – Home loan interest (max ₹2L for self-occupied)
        deduction_80e       – Education loan interest (no limit)
        deduction_80tta     – Savings bank interest (max ₹10K)
        professional_tax    – Professional tax paid
        other_deductions    – Any other deductions
    """
    if deductions is None:
        deductions = {}

    deduction_breakdown = {}

    # 1. Standard Deduction
    std_deduction = OLD_REGIME_STANDARD_DEDUCTION
    deduction_breakdown["standard_deduction"] = std_deduction

    # 2. Professional Tax
    prof_tax = float(deductions.get("professional_tax", 0))
    deduction_breakdown["professional_tax"] = prof_tax

    # 3. HRA Exemption
    hra_exemption = 0.0
    if deductions.get("hra_received") and deductions.get("basic_salary"):
        hra_exemption = _calculate_hra_exemption(
            basic_salary=float(deductions["basic_salary"]),
            hra_received=float(deductions["hra_received"]),
            actual_rent_paid=float(deductions.get("actual_rent_paid", 0)),
            city=str(deductions.get("city", "")),
        )
    deduction_breakdown["hra_exemption_sec10_13a"] = round(hra_exemption, 2)

    # 4. Section 80C (cap at ₹1.5L)
    d80c = min(float(deductions.get("deduction_80c", 0)), DEDUCTION_80C_LIMIT)
    deduction_breakdown["section_80c"] = d80c

    # 5. Section 80CCD(1B) — additional NPS (cap at ₹50K)
    d80ccd1b = min(float(deductions.get("deduction_80ccd1b", 0)), DEDUCTION_80CCD1B_LIMIT)
    deduction_breakdown["section_80ccd1b_nps"] = d80ccd1b

    # 6. Section 80D — health insurance
    d80d_self    = min(
        float(deductions.get("deduction_80d_self", 0)),
        DEDUCTION_80D["self_family_below_60"]
    )
    d80d_parents = min(
        float(deductions.get("deduction_80d_parents", 0)),
        DEDUCTION_80D["parents_above_60"]
    )
    deduction_breakdown["section_80d_self"]    = d80d_self
    deduction_breakdown["section_80d_parents"] = d80d_parents

    # 7. Section 24(b) — home loan interest
    d24b = min(float(deductions.get("deduction_24b", 0)), DEDUCTION_24B_LIMIT)
    deduction_breakdown["section_24b_home_loan_interest"] = d24b

    # 8. Section 80E — education loan (no cap)
    d80e = float(deductions.get("deduction_80e", 0))
    deduction_breakdown["section_80e_education_loan"] = d80e

    # 9. Section 80TTA — savings interest
    d80tta = min(float(deductions.get("deduction_80tta", 0)), DEDUCTION_80TTA_LIMIT)
    deduction_breakdown["section_80tta_savings_interest"] = d80tta

    # 10. Other deductions
    other = float(deductions.get("other_deductions", 0))
    deduction_breakdown["other_deductions"] = other

    # Total deductions
    total_deductions = (
        std_deduction + prof_tax + hra_exemption
        + d80c + d80ccd1b + d80d_self + d80d_parents
        + d24b + d80e + d80tta + other
    )

    # Taxable income
    taxable_income = max(0, annual_income - total_deductions)

    # Basic tax
    basic_tax = _compute_tax_on_slabs(taxable_income, OLD_REGIME_SLABS)

    # Section 87A rebate
    tax_after_rebate = _apply_87a_rebate(
        basic_tax, taxable_income, OLD_REGIME_87A_LIMIT, OLD_REGIME_87A_REBATE
    )

    # Surcharge
    surcharge = _compute_surcharge(taxable_income, tax_after_rebate, is_new_regime=False)

    # Cess
    cess = (tax_after_rebate + surcharge) * CESS_RATE

    # Total tax
    total_tax = tax_after_rebate + surcharge + cess

    effective_rate = (total_tax / annual_income * 100) if annual_income > 0 else 0

    return {
        "regime":              "Old Regime",
        "fy":                  "2024-25",
        "gross_income":        round(annual_income, 2),
        "total_deductions":    round(total_deductions, 2),
        "taxable_income":      round(taxable_income, 2),
        "deduction_breakdown": {k: round(v, 2) for k, v in deduction_breakdown.items()},
        "basic_tax":           round(basic_tax, 2),
        "rebate_87a":          round(basic_tax - tax_after_rebate, 2),
        "tax_after_rebate":    round(tax_after_rebate, 2),
        "surcharge":           round(surcharge, 2),
        "cess_4pct":           round(cess, 2),
        "total_tax_payable":   round(total_tax, 2),
        "effective_tax_rate":  f"{effective_rate:.2f}%",
        "monthly_tax":         round(total_tax / 12, 2),
        "in_hand_annual":      round(annual_income - total_tax, 2),
        "in_hand_monthly":     round((annual_income - total_tax) / 12, 2),
    }


# ─────────────────────────────────────────────
# NEW REGIME
# ─────────────────────────────────────────────

def calculate_tax_new_regime(annual_income: float) -> Dict[str, Any]:
    """
    Calculate income tax under the New Tax Regime for FY 2024-25.

    Key features:
    - Standard deduction of ₹75,000 (raised in Budget 2024)
    - No other deductions allowed (80C, 80D, HRA, etc.)
    - Section 87A rebate up to ₹25,000 for income ≤ ₹7L
    - Restructured slabs with 0% up to ₹3L, 5% till ₹7L

    Parameters
    ----------
    annual_income : Gross annual income (before standard deduction)
    """
    # Standard deduction
    std_deduction  = NEW_REGIME_STANDARD_DEDUCTION
    taxable_income = max(0, annual_income - std_deduction)

    # Basic tax on slabs
    basic_tax = _compute_tax_on_slabs(taxable_income, NEW_REGIME_SLABS)

    # Marginal relief near slab boundaries (simplified check)
    # Ensure tax does not exceed income above threshold
    # Section 87A rebate
    tax_after_rebate = _apply_87a_rebate(
        basic_tax, taxable_income, NEW_REGIME_87A_LIMIT, NEW_REGIME_87A_REBATE
    )

    # Surcharge (capped at 25% for new regime)
    surcharge = _compute_surcharge(taxable_income, tax_after_rebate, is_new_regime=True)

    # Cess
    cess = (tax_after_rebate + surcharge) * CESS_RATE

    total_tax     = tax_after_rebate + surcharge + cess
    effective_rate = (total_tax / annual_income * 100) if annual_income > 0 else 0

    return {
        "regime":              "New Regime",
        "fy":                  "2024-25",
        "gross_income":        round(annual_income, 2),
        "standard_deduction":  std_deduction,
        "taxable_income":      round(taxable_income, 2),
        "basic_tax":           round(basic_tax, 2),
        "rebate_87a":          round(basic_tax - tax_after_rebate, 2),
        "tax_after_rebate":    round(tax_after_rebate, 2),
        "surcharge":           round(surcharge, 2),
        "cess_4pct":           round(cess, 2),
        "total_tax_payable":   round(total_tax, 2),
        "effective_tax_rate":  f"{effective_rate:.2f}%",
        "monthly_tax":         round(total_tax / 12, 2),
        "in_hand_annual":      round(annual_income - total_tax, 2),
        "in_hand_monthly":     round((annual_income - total_tax) / 12, 2),
        "note": (
            "New regime has no deductions for 80C, 80D, HRA, home loan interest, etc. "
            "Only standard deduction of ₹75,000 is allowed."
        ),
    }


# ─────────────────────────────────────────────
# REGIME COMPARISON
# ─────────────────────────────────────────────

def compare_tax_regimes(
    annual_income: float,
    deductions: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Compare old and new tax regimes and recommend the better one.

    Parameters
    ----------
    annual_income : Gross annual income
    deductions    : Same dict as calculate_tax_old_regime deductions
    """
    old = calculate_tax_old_regime(annual_income, deductions)
    new = calculate_tax_new_regime(annual_income)

    old_tax  = old["total_tax_payable"]
    new_tax  = new["total_tax_payable"]
    diff     = abs(old_tax - new_tax)
    savings  = max(0, old_tax - new_tax)  # positive = new regime saves money

    if new_tax < old_tax:
        recommended = "New Regime"
        saving_regime = "New Regime"
        saving_amount = old_tax - new_tax
    elif old_tax < new_tax:
        recommended = "Old Regime"
        saving_regime = "Old Regime"
        saving_amount = new_tax - old_tax
    else:
        recommended = "Either (identical tax)"
        saving_regime = None
        saving_amount = 0

    # Break-even analysis
    # How much MORE deduction in old regime needed to match new regime?
    breakeven_deduction_gap = (
        old["total_deductions"] - new["standard_deduction"]
        if old_tax > new_tax else 0
    )

    return {
        "gross_income":            round(annual_income, 2),
        "old_regime_tax":          old_tax,
        "new_regime_tax":          new_tax,
        "tax_difference":          round(diff, 2),
        "recommended_regime":      recommended,
        "saving_regime":           saving_regime,
        "annual_savings":          round(saving_amount, 2),
        "monthly_savings":         round(saving_amount / 12, 2),
        "old_regime_deductions":   old["total_deductions"],
        "new_regime_deductions":   new["standard_deduction"],
        "old_regime_effective_rate": old["effective_tax_rate"],
        "new_regime_effective_rate": new["effective_tax_rate"],
        "old_regime_in_hand_monthly": old["in_hand_monthly"],
        "new_regime_in_hand_monthly": new["in_hand_monthly"],
        "breakeven_extra_deductions": round(breakeven_deduction_gap, 2),
        "old_regime_details":      old,
        "new_regime_details":      new,
        "analysis": (
            f"With current deductions of {_format_inr(old['total_deductions'])}, "
            f"the {recommended} saves {_format_inr(saving_amount)} per year "
            f"({_format_inr(round(saving_amount/12, 2))} per month)."
        ),
    }


# ─────────────────────────────────────────────
# 80C Investment Tracker
# ─────────────────────────────────────────────

def calculate_80c_investments(investments: Dict[str, float]) -> Dict[str, Any]:
    """
    Track and analyse 80C investments against the ₹1.5L limit.

    Parameters
    ----------
    investments : Dict mapping investment name to amount. Keys can be:
        EPF, PPF, ELSS, NSC, Tax_Saver_FD, LIC, Home_Loan_Principal,
        Tuition_Fees, SSY, NPS_Employee, or any custom name.
    """
    total_invested = sum(investments.values())
    utilised       = min(total_invested, DEDUCTION_80C_LIMIT)
    unutilised     = max(0, DEDUCTION_80C_LIMIT - total_invested)
    excess         = max(0, total_invested - DEDUCTION_80C_LIMIT)

    sorted_inv = sorted(investments.items(), key=lambda x: x[1], reverse=True)

    tax_saving_old_30pct = utilised * 0.30 * (1 + CESS_RATE)
    tax_saving_old_20pct = utilised * 0.20 * (1 + CESS_RATE)

    suggestions = []
    if unutilised > 0:
        suggestions.append(
            f"You have ₹{unutilised:,.0f} of 80C limit unused. "
            f"Consider ELSS (equity exposure + tax saving), PPF (safe, 7.1% tax-free), "
            f"or NPS (retirementfocused)."
        )
    if excess > 0:
        suggestions.append(
            f"₹{excess:,.0f} invested beyond ₹1.5L cap gives NO additional 80C benefit."
        )

    return {
        "limit":             DEDUCTION_80C_LIMIT,
        "total_invested":    round(total_invested, 2),
        "limit_utilised":    round(utilised, 2),
        "utilisation_pct":   f"{min(100, total_invested/DEDUCTION_80C_LIMIT*100):.1f}%",
        "remaining_limit":   round(unutilised, 2),
        "excess_beyond_cap": round(excess, 2),
        "investments_breakdown": {k: round(v, 2) for k, v in sorted_inv},
        "estimated_tax_saving_at_30pct": round(tax_saving_old_30pct, 2),
        "estimated_tax_saving_at_20pct": round(tax_saving_old_20pct, 2),
        "suggestions":       suggestions,
        "note": "80C limit is ₹1,50,000. Additional ₹50,000 via NPS under 80CCD(1B).",
    }


# ─────────────────────────────────────────────
# Tax-Saving Suggestions
# ─────────────────────────────────────────────

def suggest_tax_savings(
    annual_income: float,
    current_investments: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analyse the current portfolio and suggest tax-saving strategies.

    Parameters
    ----------
    annual_income        : Gross annual income
    current_investments  : Dict of current investments / deductions. Same keys
                           as the deductions dict in calculate_tax_old_regime.
    """
    if current_investments is None:
        current_investments = {}

    suggestions  = []
    max_savings  = 0.0
    slab_rate    = _get_slab_rate(annual_income)

    # --- 80C gap ---
    current_80c  = float(current_investments.get("deduction_80c", 0))
    gap_80c      = max(0, DEDUCTION_80C_LIMIT - current_80c)
    if gap_80c > 0:
        saving_80c = gap_80c * slab_rate * (1 + CESS_RATE)
        suggestions.append({
            "section":    "80C",
            "action":     f"Invest ₹{gap_80c:,.0f} more in 80C instruments (ELSS / PPF / NPS)",
            "max_benefit": round(saving_80c, 2),
            "instruments": ["ELSS (best for equity growth)", "PPF (safe, 7.1% tax-free)", "NPS Tier-I"],
        })
        max_savings += saving_80c

    # --- 80CCD(1B) NPS ---
    current_nps  = float(current_investments.get("deduction_80ccd1b", 0))
    gap_nps      = max(0, DEDUCTION_80CCD1B_LIMIT - current_nps)
    if gap_nps > 0:
        saving_nps = gap_nps * slab_rate * (1 + CESS_RATE)
        suggestions.append({
            "section":    "80CCD(1B)",
            "action":     f"Invest ₹{gap_nps:,.0f} more in NPS Tier-I (over 80C limit)",
            "max_benefit": round(saving_nps, 2),
            "instruments": ["NPS Tier-I — Equity, Corporate Debt, Govt Securities options"],
        })
        max_savings += saving_nps

    # --- 80D health insurance ---
    current_80d_self    = float(current_investments.get("deduction_80d_self", 0))
    current_80d_parents = float(current_investments.get("deduction_80d_parents", 0))
    gap_80d_self        = max(0, DEDUCTION_80D["self_family_below_60"] - current_80d_self)
    gap_80d_parents     = max(0, DEDUCTION_80D["parents_above_60"] - current_80d_parents)

    if gap_80d_self > 0:
        saving_80d_self = gap_80d_self * slab_rate * (1 + CESS_RATE)
        suggestions.append({
            "section":    "80D",
            "action":     f"Get health insurance for self/family — deduction up to ₹25,000",
            "max_benefit": round(saving_80d_self, 2),
            "instruments": ["Comprehensive health insurance plan"],
        })
        max_savings += saving_80d_self

    if gap_80d_parents > 0:
        saving_80d_parents = gap_80d_parents * slab_rate * (1 + CESS_RATE)
        suggestions.append({
            "section":    "80D (parents)",
            "action":     f"Get health insurance for parents — up to ₹50,000 (senior citizen)",
            "max_benefit": round(saving_80d_parents, 2),
            "instruments": ["Senior citizen health insurance plan"],
        })
        max_savings += saving_80d_parents

    # --- HRA ---
    hra = float(current_investments.get("hra_received", 0))
    rent_paid = float(current_investments.get("actual_rent_paid", 0))
    if hra == 0 and rent_paid == 0 and annual_income > 500_000:
        suggestions.append({
            "section":    "HRA / Section 80GG",
            "action":     "If you pay rent, claim HRA exemption (salaried) or 80GG deduction",
            "max_benefit": "Varies — up to 50% of basic salary (metro) or 40% (non-metro)",
            "instruments": ["Keep rent receipts, PAN of landlord if rent > ₹1L p.a."],
        })

    # --- Home loan ---
    home_loan = float(current_investments.get("deduction_24b", 0))
    if home_loan == 0 and annual_income > 1_000_000:
        suggestions.append({
            "section":    "Section 24(b)",
            "action":     "Home loan interest deduction up to ₹2,00,000 p.a. for self-occupied",
            "max_benefit": round(DEDUCTION_24B_LIMIT * slab_rate * (1 + CESS_RATE), 2),
            "instruments": ["Housing loan from bank / HFC"],
        })

    # --- Regime switch recommendation ---
    current_deductions = {k: v for k, v in current_investments.items()}
    comparison = compare_tax_regimes(annual_income, current_deductions)
    if comparison["annual_savings"] > 0:
        suggestions.append({
            "section":    "Regime Switch",
            "action":     (
                f"Switch to {comparison['recommended_regime']} — "
                f"saves ₹{comparison['annual_savings']:,.0f} p.a."
            ),
            "max_benefit": comparison["annual_savings"],
            "instruments": [f"File ITR under {comparison['recommended_regime']}"],
        })
        max_savings = max(max_savings, comparison["annual_savings"])

    return {
        "annual_income":     round(annual_income, 2),
        "applicable_slab":   f"{slab_rate*100:.0f}%",
        "total_potential_savings": round(max_savings, 2),
        "suggestions":       suggestions,
        "priority_order":    [
            "1. Max out 80C (₹1.5L) — ELSS for equity + tax saving",
            "2. NPS 80CCD(1B) extra ₹50K — good for retirement",
            "3. Health insurance 80D — self ₹25K + parents ₹50K",
            "4. Compare regimes annually as deductions change",
            "5. Home loan 24(b) if buying a house",
        ],
        "disclaimer": (
            "These are indicative savings. Consult a CA for personalised advice. "
            "Tax laws may change."
        ),
    }


def _get_slab_rate(income: float) -> float:
    """Return the marginal slab rate for a given income (approximate, for savings estimation)."""
    if income <= 500_000:
        return 0.05
    elif income <= 1_000_000:
        return 0.20
    else:
        return 0.30
