# Fama-French Multi-Factor Risk Decomposition

## Problem Statement

CAPM explains stock returns using a single risk factor: exposure to the broad market. But in
practice, a meaningful portion of a stock's return behavior is driven by *style* factors — how
"small" or "large" a company is (size), and whether it behaves like a value stock or a growth
stock (value/growth). This project builds up a factor-based risk model in two stages:

1. **Single-stock analysis (AAPL):** Compare a CAPM (market-only) model against a Fama-French
   3-factor model to see how much additional risk is explained once size and value are added.
2. **Portfolio extension (8 stocks):** Re-run the same comparison on a diversified, equal-weighted
   portfolio to test whether factor loadings become more statistically reliable once
   company-specific noise is averaged out.

This mirrors how real risk teams work: start by understanding a single position's risk drivers,
then scale the same framework up to a portfolio.

## Workflow

### Stage 1 : Single Stock: CAPM vs. Fama-French 3-Factor (AAPL)

The first stage answers a narrow question: for one stock, how much of its return variation is
explained by market risk alone, versus market + size + value risk combined?

- Pull AAPL monthly returns and Fama-French factor data (Mkt-RF, SMB, HML, RF) over the same period
- Run a CAPM regression: `excess_return = alpha + beta(Mkt-RF)`
- Run a 3-factor regression: `excess_return = alpha + b1(Mkt-RF) + b2(SMB) + b3(HML)`
- Compare R², adjusted R², and the significance of each factor loading

This stage produces the baseline factor profile for a single name, and — importantly — surfaces a
limitation: single-stock regressions carry a lot of idiosyncratic, company-specific noise, which
can make secondary factors like SMB appear statistically insignificant even when a broader size
effect might genuinely be present.

### Stage 2 : Portfolio Extension: 8-Stock Equal-Weighted Portfolio

To test whether that insignificance was a single-stock noise artifact rather than a real absence
of size-factor exposure, the same 3-factor model is re-run on an equal-weighted portfolio of
8 stocks, deliberately spread across sectors to diversify away idiosyncratic risk:

- **AAPL** (Technology)
- **MSFT** (Technology)
- **JNJ** (Healthcare)
- **XOM** (Energy)
- **JPM** (Financials)
- **PG** (Consumer Staples)
- **KO** (Consumer Staples)
- **CAT** (Industrials)

Equal-weighting keeps the exercise simple and avoids having to justify weighting assumptions —
the goal here isn't to build an optimal portfolio, it's to isolate the effect of diversification
on the *statistical reliability* of the factor estimates.

The single-stock and portfolio results are then compared side by side — coefficients, standard
errors, and p-values — to see whether:
- Standard errors shrink once idiosyncratic noise is averaged out across 8 names
- SMB's significance improves (or at least its p-value drops meaningfully)
- Any factor flips from insignificant to significant, or vice versa

### Why This Sequencing Matters

Going single-stock → portfolio isn't just a bigger dataset — it's a deliberate test of *when
factor models are reliable*. Fama-French factors were built and validated on diversified
portfolios, not individual names, so this workflow directly demonstrates that limitation rather
than just asserting it.

## Data
- **Stock/portfolio returns:** `yfinance`, monthly frequency
- **Factor returns:** Fama-French 3-factor data from Kenneth French's Data Library
  (Mkt-RF, SMB, HML, RF), via `pandas_datareader`
- **Period:** 01/01/2015 - 01/01/2025

## Key Files
- `src/factor_data_loader.py` — pulls single-stock and portfolio returns, aligns with FF factors
  - `build_factor_dataset()` — single-stock version
  - `build_portfolio_factor_dataset()` — equal-weighted 8-stock portfolio version
- `src/factor_model.py` — runs CAPM and 3-factor regressions, compares them side by side
- `notebooks/factor_analysis.ipynb` — full walkthrough: single-stock analysis, then portfolio
  extension, then side-by-side comparison
- `outputs/` — saved charts and comparison tables

## Findings

### Stage 1 :- Single Stock (AAPL)
- CAPM R²: **0.46**
- 3-Factor R²: **0.53**
- Factor loadings: Mkt-RF **[β, p-value]**, SMB **[β, p-value]**, HML **[β, p-value]**
- Which factors were statistically significant, and which weren't?

### Stage 2 :- Portfolio (8 Stocks)
- 3-Factor R²: **0.876074**
- Factor loadings: Mkt-RF **0.882786, p = 0.000**, SMB **0.288700, p = 0.000**, HML **0.241438, p =  0.000** 
- Did standard errors shrink relative to the single-stock case? Did SMB's significance improve?

## So What? (Risk Relevance)

This two-stage workflow mirrors a real judgment call risk teams make constantly: how much
confidence to place in a factor exposure estimate depends on *what it was estimated on*. A
single-position factor loading carries more estimation uncertainty than the same loading
estimated on a diversified book — which matters directly for how confidently a risk team can act
on a single name's factor exposure versus a portfolio-level one.

[Fill in with your specific comparison once you've run both stages — e.g., "SMB's standard error
fell by X% moving from the single-stock to the portfolio regression, supporting the idea that the
single-name insignificance was largely a noise artifact rather than a genuine absence of size risk."]

## How to Run
```bash
pip install -r requirements.txt
python src/factor_data_loader.py
jupyter notebook notebooks/factor_analysis.ipynb
```

## Next Steps / Extensions
- Extend to 5-factor model (add RMW profitability, CMA investment factors)
- Test alternative portfolio weightings (market-cap weighted vs. equal-weighted) to see whether
  weighting scheme affects factor loading stability
