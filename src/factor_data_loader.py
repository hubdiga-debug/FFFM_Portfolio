"""
factor_data_loader.py
Pulls stock returns and Fama-French 3-factor data, aligns them on date.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import pandas_datareader.data as web
import os


def download_stock_monthly_returns(ticker: str, start: str, end: str) -> pd.Series:
    """
    Downloads monthly returns for a given ticker.
    Robust to yfinance sometimes returning MultiIndex columns even for a single ticker.
    """
    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

    close = raw["Close"]
    if isinstance(close, pd.DataFrame):
        # MultiIndex column case (e.g., columns = [('Close', 'AAPL')]) -> squeeze to Series
        close = close.squeeze()
    close.name = "stock_return"  # placeholder name, overwritten below anyway

    monthly_prices = close.resample("ME").last()
    returns = monthly_prices.pct_change().dropna()
    returns.name = "stock_return"
    return returns


def download_portfolio_monthly_returns(tickers: list, start: str, end: str) -> pd.Series:
    """
    Downloads monthly returns for multiple tickers and combines them into a single
    equal-weighted portfolio return series.

    Equal-weighting is a deliberate simplification: it keeps the comparison against the
    single-stock case clean (no need to justify weight choices) while still averaging away
    a meaningful amount of idiosyncratic, company-specific noise.
    """
    raw = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=True)["Close"]

    # raw is a DataFrame with one column per ticker when multiple tickers are passed
    monthly_prices = raw.resample("ME").last()
    individual_returns = monthly_prices.pct_change().dropna()

    portfolio_returns = individual_returns.mean(axis=1)  # equal-weighted average across tickers
    portfolio_returns.name = "stock_return"
    return portfolio_returns


def download_fama_french_factors(start: str, end: str) -> pd.DataFrame:
    """
    Downloads Fama-French 3-factor monthly data from Kenneth French's Data Library.
    Returns Mkt-RF, SMB, HML, RF as decimals (source data is in percent).
    """
    ff = web.DataReader("F-F_Research_Data_Factors", "famafrench", start=start, end=end)[0]
    ff = ff / 100.0  # convert from percent to decimal
    ff.index = ff.index.to_timestamp(how="end").normalize()  # PeriodIndex -> month-end Timestamp
                                                              # (avoids deprecated 'M' freq alias)
    return ff


def build_factor_dataset(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Builds a combined DataFrame of stock excess returns and Fama-French factors, aligned on date.
    Single-stock version.
    """
    stock_returns = download_stock_monthly_returns(ticker, start, end)
    ff_factors = download_fama_french_factors(start, end)

    df = pd.concat([stock_returns, ff_factors], axis=1).dropna()
    df["excess_return"] = df["stock_return"] - df["RF"]

    return df


def build_portfolio_factor_dataset(tickers: list, start: str, end: str) -> pd.DataFrame:
    """
    Builds a combined DataFrame of equal-weighted portfolio excess returns and
    Fama-French factors, aligned on date. Portfolio version — use this to compare
    factor loading stability/significance against the single-stock case.
    """
    portfolio_returns = download_portfolio_monthly_returns(tickers, start, end)
    ff_factors = download_fama_french_factors(start, end)

    df = pd.concat([portfolio_returns, ff_factors], axis=1).dropna()
    df["excess_return"] = df["stock_return"] - df["RF"]

    return df


if __name__ == "__main__":
    TICKER = "AAPL"        # change to your chosen ticker
    PORTFOLIO_TICKERS = ["AAPL", "MSFT", "JNJ", "XOM", "JPM", "PG", "KO", "CAT"]  # diversified across sectors
    START = "2015-01-01"
    END = "2025-01-01"

    os.makedirs("data", exist_ok=True)

    # Single-stock dataset
    df_single = build_factor_dataset(TICKER, START, END)
    single_path = f"data/{TICKER}_factor_data.csv"
    df_single.to_csv(single_path)
    print(f"Saved {len(df_single)} rows of single-stock factor data to {single_path}")

    # Portfolio dataset
    df_portfolio = build_portfolio_factor_dataset(PORTFOLIO_TICKERS, START, END)
    portfolio_path = "data/portfolio_factor_data.csv"
    df_portfolio.to_csv(portfolio_path)
    print(f"Saved {len(df_portfolio)} rows of portfolio factor data to {portfolio_path}")
