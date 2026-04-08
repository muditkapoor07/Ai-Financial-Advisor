"""
Tax data for India - FY 2024-25 (Assessment Year 2025-26)
Reflects Union Budget 2024 changes.
"""

# ─────────────────────────────────────────────
# NEW REGIME TAX SLABS  (FY 2024-25)
# Section 115BAC — default regime from FY 2023-24 onwards
# Budget 2024: slab restructured, rebate u/s 87A raised to ₹25,000
# ─────────────────────────────────────────────
NEW_REGIME_SLABS = [
    # (upper_limit, rate)  — lower limit is previous upper_limit + 1
    (300_000,    0.00),   # Up to ₹3,00,000      → 0%
    (700_000,    0.05),   # ₹3,00,001 – ₹7,00,000 → 5%
    (1_000_000,  0.10),   # ₹7,00,001 – ₹10,00,000 → 10%
    (1_200_000,  0.15),   # ₹10,00,001 – ₹12,00,000 → 15%
    (1_500_000,  0.20),   # ₹12,00,001 – ₹15,00,000 → 20%
    (float('inf'), 0.30), # Above ₹15,00,000 → 30%
]

# Standard deduction under new regime (introduced from FY 2023-24)
NEW_REGIME_STANDARD_DEDUCTION = 75_000  # ₹75,000 (Budget 2024, raised from ₹50,000)

# Section 87A rebate — new regime
NEW_REGIME_87A_LIMIT   = 700_000   # Income up to ₹7,00,000
NEW_REGIME_87A_REBATE  = 25_000    # Maximum rebate ₹25,000

# ─────────────────────────────────────────────
# OLD REGIME TAX SLABS  (FY 2024-25)
# ─────────────────────────────────────────────
OLD_REGIME_SLABS = [
    (250_000,    0.00),   # Up to ₹2,50,000      → 0%
    (500_000,    0.05),   # ₹2,50,001 – ₹5,00,000 → 5%
    (1_000_000,  0.20),   # ₹5,00,001 – ₹10,00,000 → 20%
    (float('inf'), 0.30), # Above ₹10,00,000 → 30%
]

# Standard deduction — old regime (salaried / pensioners)
OLD_REGIME_STANDARD_DEDUCTION = 50_000  # ₹50,000

# Section 87A rebate — old regime
OLD_REGIME_87A_LIMIT  = 500_000   # Income up to ₹5,00,000
OLD_REGIME_87A_REBATE = 12_500    # Maximum rebate ₹12,500

# ─────────────────────────────────────────────
# SURCHARGE RATES  (same for both regimes)
# ─────────────────────────────────────────────
SURCHARGE_RATES = [
    # (income_threshold, surcharge_rate)
    (5_000_000,   0.00),   # Up to ₹50L    → nil
    (10_000_000,  0.10),   # ₹50L – ₹1 Cr → 10%
    (20_000_000,  0.15),   # ₹1Cr – ₹2Cr  → 15%
    (50_000_000,  0.25),   # ₹2Cr – ₹5Cr  → 25%  (new regime cap at 25%)
    (float('inf'), 0.37),  # Above ₹5Cr   → 37%  (old regime only; new regime capped at 25%)
]

NEW_REGIME_SURCHARGE_CAP = 0.25  # New regime surcharge capped at 25%

# Health and Education Cess
CESS_RATE = 0.04  # 4% on (tax + surcharge)

# ─────────────────────────────────────────────
# DEDUCTION LIMITS  (old regime)
# ─────────────────────────────────────────────

# Section 80C — aggregate limit
DEDUCTION_80C_LIMIT = 150_000  # ₹1,50,000

# Section 80C eligible investments / payments
DEDUCTION_80C_ITEMS = {
    "EPF":                "Employee Provident Fund contribution",
    "PPF":                "Public Provident Fund",
    "ELSS":               "Equity Linked Savings Scheme (3-yr lock-in)",
    "NSC":                "National Savings Certificate",
    "Tax Saver FD":       "5-year tax-saver bank FD",
    "Life Insurance":     "LIC / term plan premiums",
    "Home Loan Principal":"Repayment of housing loan principal",
    "Tuition Fees":       "Children's tuition fees (max 2 children)",
    "SSY":                "Sukanya Samriddhi Yojana",
    "NPS Employee":       "NPS Tier-I employee contribution (u/s 80CCD(1))",
}

# Section 80CCD(1B) — additional NPS contribution (over and above 80C)
DEDUCTION_80CCD1B_LIMIT = 50_000   # ₹50,000

# Section 80CCD(2) — employer NPS contribution (not part of 80C ceiling)
# Up to 10% of basic salary for private employees; 14% for govt employees
DEDUCTION_80CCD2_RATE_PRIVATE = 0.10
DEDUCTION_80CCD2_RATE_GOVT    = 0.14

# Section 80D — health insurance premiums
DEDUCTION_80D = {
    "self_family_below_60":    25_000,  # Self + family (all below 60)
    "self_family_above_60":    50_000,  # Self or spouse above 60
    "parents_below_60":        25_000,  # Parents below 60
    "parents_above_60":        50_000,  # Parents above 60 (senior citizen)
    "preventive_health_checkup": 5_000, # Within overall 80D limit
}

# Section 80D — total maximum for self + parents (both senior citizens)
DEDUCTION_80D_MAX = 100_000  # ₹1,00,000

# Section 80E — education loan interest
DEDUCTION_80E_LIMIT = None  # No upper limit; entire interest is deductible

# Section 80EEA — first-time home buyer interest (stamp duty ≤ ₹45L)
DEDUCTION_80EEA_LIMIT = 150_000  # ₹1,50,000 (over and above 24(b))

# Section 24(b) — home loan interest (self-occupied)
DEDUCTION_24B_LIMIT = 200_000  # ₹2,00,000

# Section 80G — donations
DEDUCTION_80G_RATES = {
    "100_percent_no_limit":  1.00,
    "50_percent_no_limit":   0.50,
    "100_percent_with_limit": 1.00,  # restricted to 10% of adjusted GTI
    "50_percent_with_limit":  0.50,  # restricted to 10% of adjusted GTI
}

# Section 80TTA — savings account interest (non-senior citizen)
DEDUCTION_80TTA_LIMIT = 10_000  # ₹10,000

# Section 80TTB — interest income (senior citizens — replaces 80TTA)
DEDUCTION_80TTB_LIMIT = 50_000  # ₹50,000

# HRA exemption rules (Section 10(13A))
HRA_EXEMPTION_RULES = {
    "metro_cities":        ["Mumbai", "Delhi", "Kolkata", "Chennai"],
    "metro_hra_percent":   0.50,   # 50% of basic salary in metro
    "non_metro_hra_percent": 0.40, # 40% of basic salary in non-metro
    # Exempt = min(actual HRA, 50/40% of basic, actual rent – 10% of basic)
}

# ─────────────────────────────────────────────
# CAPITAL GAINS RATES  (FY 2024-25, post Budget 2024)
# ─────────────────────────────────────────────
CAPITAL_GAINS = {
    # Equity / equity MF (STT paid)
    "STCG_equity":         0.20,   # Budget 2024: raised from 15% → 20%
    "LTCG_equity":         0.125,  # Budget 2024: raised from 10% → 12.5%
    "LTCG_equity_exemption": 125_000,  # ₹1,25,000 (raised from ₹1L)

    # Debt MF / bonds (non-equity)
    "STCG_debt":           "slab", # Taxed at slab rate
    "LTCG_debt":           0.125,  # Flat 12.5% without indexation (post Jul 23, 2024)

    # Real estate (immovable property)
    "STCG_property":       "slab", # < 2 years; taxed at slab rate
    "LTCG_property":       0.125,  # ≥ 2 years; flat 12.5% without indexation (Budget 2024)
    "LTCG_property_old":   0.20,   # Pre-Jul 23, 2024 — with indexation option
}

# ─────────────────────────────────────────────
# OTHER REFERENCE RATES
# ─────────────────────────────────────────────
PROFESSIONAL_TAX_MAX    =  2_400   # Maximum ₹2,400 p.a. (state levy)
PRESUMPTIVE_TAX_44ADA   =  0.50    # 50% of gross receipts for professionals
PRESUMPTIVE_TAX_44AD    =  0.08    # 8% of turnover for businesses (6% digital)

TDS_SALARY_SECTION      =  "192"
TDS_FD_SECTION          =  "194A"
TDS_FD_RATE             =  0.10    # 10% for residents; higher for non-PAN
TDS_FD_THRESHOLD        =  40_000  # ₹40,000 (₹50,000 for senior citizens)

# ─────────────────────────────────────────────
# CONVENIENCE DICT for display
# ─────────────────────────────────────────────
TAX_SUMMARY = {
    "FY": "2024-25",
    "AY": "2025-26",
    "new_regime_default": True,
    "new_regime_standard_deduction": NEW_REGIME_STANDARD_DEDUCTION,
    "old_regime_standard_deduction": OLD_REGIME_STANDARD_DEDUCTION,
    "cess": f"{CESS_RATE*100:.0f}%",
    "80C_limit": DEDUCTION_80C_LIMIT,
    "80CCD1B_limit": DEDUCTION_80CCD1B_LIMIT,
    "80D_self_limit": DEDUCTION_80D["self_family_below_60"],
    "80D_parents_limit": DEDUCTION_80D["parents_above_60"],
}
