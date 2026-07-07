"""
factor_model.py
Single-factor (CAPM) and multi-factor (Fama-French 3-factor) regression functions,
with a direct comparison between the two.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm


def run_capm(df: pd.DataFrame) -> dict:
    """
    Single-factor CAPM using excess returns:
    excess_return = alpha + beta * (Mkt-RF) + epsilon
    """
    X = sm.add_constant(df["Mkt-RF"])
    y = df["excess_return"]

    model = sm.OLS(y, X).fit()

    return {
        "alpha": model.params["const"],
        "beta_mkt": model.params["Mkt-RF"],
        "r_squared": model.rsquared,
        "model": model,
    }


def run_three_factor_model(df: pd.DataFrame) -> dict:
    """
    Fama-French 3-factor model:
    excess_return = alpha + b1(Mkt-RF) + b2(SMB) + b3(HML) + epsilon
    """
    X = sm.add_constant(df[["Mkt-RF", "SMB", "HML"]])
    y = df["excess_return"]

    model = sm.OLS(y, X).fit()

    return {
        "alpha": model.params["const"],
        "beta_mkt": model.params["Mkt-RF"],
        "beta_smb": model.params["SMB"],
        "beta_hml": model.params["HML"],
        "r_squared": model.rsquared,
        "model": model,
    }


def compare_models(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs both models and returns a side-by-side comparison table.
    """
    capm = run_capm(df)
    ff3 = run_three_factor_model(df)

    comparison = pd.DataFrame({
        "CAPM": {
            "Alpha": capm["alpha"],
            "Beta (Mkt-RF)": capm["beta_mkt"],
            "Beta (SMB)": np.nan,
            "Beta (HML)": np.nan,
            "R-squared": capm["r_squared"],
        },
        "Fama-French 3-Factor": {
            "Alpha": ff3["alpha"],
            "Beta (Mkt-RF)": ff3["beta_mkt"],
            "Beta (SMB)": ff3["beta_smb"],
            "Beta (HML)": ff3["beta_hml"],
            "R-squared": ff3["r_squared"],
        },
    })

    return comparison, capm, ff3


if __name__ == "__main__":
    TICKER = "AAPL"
    df = pd.read_csv(f"data/{TICKER}_factor_data.csv", index_col=0, parse_dates=True)

    comparison, capm_result, ff3_result = compare_models(df)

    print("Model Comparison")
    print(comparison)
    print()
    print("Full Fama-French 3-Factor Summary")
    print(ff3_result["model"].summary())

    comparison.to_csv("outputs/model_comparison.csv")
    print("\nComparison table saved to outputs/model_comparison.csv")
