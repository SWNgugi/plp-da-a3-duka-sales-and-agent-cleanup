"""Cleaning pipeline for the mobile-money agent transaction extract."""
import numpy as np
import pandas as pd

VALID_TYPES = {"deposit": "Deposit", "withdrawal": "Withdrawal"}


def clean_agent_data(txns, agents):
    """Clean the raw agent transactions and merge them with the agent register.

    Rules applied (each one is written to the log):
      1. Remove duplicate transactions (same txn_id, first occurrence kept).
      2. Standardise txn_type to exactly 'Deposit' / 'Withdrawal'.
      3. Convert amount to numeric (text such as 'N/A' becomes missing).
      4. Parse txn_date to datetime (handles YYYY-MM-DD and YYYY/MM/DD).
      5. Impute missing amounts with the median amount of the same txn_type
         and set amount_imputed = True.
      6. Flag outliers with the IQR rule (is_outlier), computed on real amounts.
      7. Left-join to the agent register; unknown agents get county 'Unknown'.

    Parameters
    ----------
    txns : pandas.DataFrame   raw transactions (as read from agent_transactions.csv)
    agents : pandas.DataFrame agent register (as read from agents.csv)

    Returns
    -------
    (clean_df, log) : (pandas.DataFrame, pandas.DataFrame)
    """
    log = []

    def record(rule, rows_affected, action):
        log.append({"step": len(log) + 1, "rule": rule,
                    "rows_affected": int(rows_affected), "action": action})

    df = txns.copy()
    record("Input", len(df), f"{len(df)} raw transaction rows loaded")

    # 1. Uniqueness
    dup_mask = df.duplicated(subset="txn_id", keep="first")
    df = df.loc[~dup_mask].copy()
    record("Duplicate txn_id", dup_mask.sum(), "Removed, first occurrence kept")

    # 2. Consistency of txn_type
    cleaned_type = df["txn_type"].astype(str).str.strip().str.lower().map(VALID_TYPES)
    changed = (cleaned_type != df["txn_type"]).sum()
    if cleaned_type.isna().any():
        raise ValueError(f"Unmapped txn_type values: {df.loc[cleaned_type.isna(), 'txn_type'].unique()}")
    df["txn_type"] = cleaned_type
    record("Inconsistent txn_type", changed, "Trimmed, lower-cased and mapped to Deposit/Withdrawal")

    # 3. Validity of amount
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    missing = df["amount"].isna()
    record("Missing/invalid amount", missing.sum(), "Converted to numeric; invalid text became NaN")

    # 4. Validity of dates
    df["txn_date"] = pd.to_datetime(df["txn_date"].astype(str).str.replace("/", "-"),
                                    format="%Y-%m-%d", errors="coerce")
    bad_dates = df["txn_date"].isna().sum()
    record("Unparseable txn_date", bad_dates, "Slash dates converted to ISO; unparseable set to NaT")
    df = df.dropna(subset=["txn_date"]).copy() if bad_dates else df

    # 5. Completeness: median imputation by txn_type + flag
    df["amount_imputed"] = missing.loc[df.index]
    medians = df.loc[~df["amount_imputed"]].groupby("txn_type")["amount"].median()
    df["amount"] = df["amount"].fillna(df["txn_type"].map(medians))
    record("Imputed amount", df["amount_imputed"].sum(),
           "Filled with median amount of same txn_type; amount_imputed = True")

    # 6. Outliers (IQR on real, non-imputed amounts)
    real = df.loc[~df["amount_imputed"], "amount"]
    q1, q3 = real.quantile([0.25, 0.75])
    upper = q3 + 1.5 * (q3 - q1)
    lower = q1 - 1.5 * (q3 - q1)
    df["is_outlier"] = (~df["amount_imputed"]) & ((df["amount"] > upper) | (df["amount"] < lower))
    record("Outlier amount (IQR)", df["is_outlier"].sum(),
           f"Flagged, not removed; fences {lower:,.0f} to {upper:,.0f}")

    # 7. Merge with agent register
    n_before = len(df)
    register = agents.drop_duplicates(subset="agent_id")
    df = df.merge(register[["agent_id", "county"]], on="agent_id", how="left", validate="m:1")
    assert len(df) == n_before, "Merge changed the row count"
    df["unknown_agent"] = df["county"].isna()
    df["county"] = df["county"].fillna("Unknown")
    record("Unknown agent_id", df["unknown_agent"].sum(),
           "Kept; county set to 'Unknown' so totals still reconcile")

    record("Output", len(df), f"{len(df)} clean rows")
    return df.reset_index(drop=True), pd.DataFrame(log)
