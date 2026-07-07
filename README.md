# Fama-French Multi-Factor Risk Decomposition

## Problem Statement
CAPM explains returns with a single factor (market beta). But real risk isn't just market
exposure — it's exposure to *style factors* like size and value. This project decomposes a
stock's (or portfolio's) returns into the Fama-French 3-factor model and compares it directly
against the single-factor CAPM baseline from the companion project.

**Risk question being answered:** How much of [TICKER]'s return variation is explained by
market risk alone vs. market + size + value risk? Which factor exposures matter most, and are
they statistically reliable?

## Data
- **Stock/portfolio returns:** same source as CAPM project (`yfinance`)
- **Factor returns:** Fama-French 3-factor data from Kenneth French's Data Library
  (Mkt-RF, SMB, HML, RF) — downloaded via `pandas_datareader.famafrench`
- **Period:** [match your CAPM project period for direct comparison]
- **Frequency:** Monthly (Fama-French factors are most reliably available monthly; weekly/daily
  exists but monthly is the standard convention for this model)

## Methodology
1. Pull stock returns and Fama-French factor data, align on date
2. Compute excess stock return: R_i − Rf
3. Run multiple linear regression:

   R_i − Rf = α + β₁(Mkt-RF) + β₂(SMB) + β₃(HML) + ε

4. Compare against single-factor CAPM (R² improvement, factor significance)
5. Residual diagnostics — check if adding factors actually explains previously unexplained variation

## Key Files
- `src/factor_data_loader.py` — pulls stock returns + Fama-French factors, aligns on date
- `src/factor_model.py` — runs single-factor and multi-factor regressions, compares them
- `notebooks/factor_analysis.ipynb` — full walkthrough with plots and commentary
- `outputs/` — saved charts and comparison tables

## Findings
> Fill in after running the analysis. Example structure:
- CAPM (market-only) R²: **[value]**
- 3-Factor R²: **[value]** — an improvement of [X] percentage points
- Factor loadings:
  - Market (Mkt-RF): **[β, significance]**
  - Size (SMB): **[β, significance]** — positive/negative tilt toward small-cap or large-cap
  - Value (HML): **[β, significance]** — positive/negative tilt toward value or growth
- Which factor(s) were statistically significant vs. noise?

## So What? (Risk Relevance)
This is a simplified version of what commercial risk systems (MSCI Barra, Axioma, Bloomberg PORT)
do at scale: decompose portfolio risk into factor exposures so a risk team can answer "where is
this risk coming from?" rather than just "how much risk is there?"

Example interpretation: [e.g., "The stock shows a significant negative loading on HML, meaning
it behaves like a growth stock — if value factors sell off, this position is not the one that
benefits, and if growth factors reverse, this position carries that risk directly."]

A single-factor CAPM view would have missed this — it only tells you overall market sensitivity,
not *which* style risk is embedded in the exposure.

## How to Run
```bash
pip install -r requirements.txt
python src/factor_data_loader.py
jupyter notebook notebooks/factor_analysis.ipynb
```

## Next Steps / Extensions
- ✅ **Portfolio vs. single-stock comparison** — implemented in this repo. See `build_portfolio_factor_dataset()`
  in `src/factor_data_loader.py` and Section 6 of the notebook. Runs the same 3-factor model on an
  equal-weighted 8-stock portfolio to test whether averaging away idiosyncratic noise produces
  tighter, more reliable factor loadings (particularly for SMB, which is often insignificant for
  single mega-cap names).
- Extend to 5-factor model (add RMW profitability, CMA investment factors)
- Compare factor exposure stability over rolling windows (link back to CAPM project's rolling beta idea)

### Extension Findings: Single Stock vs. Portfolio
> Fill in after running Section 6 of the notebook. Example structure:
- Single-stock SMB: coef = [value], std err = [value], p = [value] (insignificant)
- Portfolio SMB: coef = [value], std err = [value], p = [value] ([significant/still insignificant])
- Interpretation: [e.g., "Standard error on SMB shrank by X% moving from single stock to portfolio,
  supporting the idea that idiosyncratic noise — not a true absence of size-factor exposure — was
  driving the insignificance in the single-name regression."]
