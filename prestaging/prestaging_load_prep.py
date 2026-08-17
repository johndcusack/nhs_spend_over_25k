import pandas as pd
import hashlib
from prestaging.prestaging_config import PROVIDER_CONFIGS, CUSTOM_READERS, DOWNLOAD_DIR, ProviderConfig
# rework config to have a column order for sorting each org's columns
# 
def normalise_df(df: pd.DataFrame, config: ProviderConfig) -> pd.DataFrame:
    """
    Normalise a dataframe for hashing. 
    Coercions here are just for ensuring consistent hashing and are not
    written back to the dataframes themselves
    """
    expected_cols = set(config.column_spec.keys())
    actual_cols = set(df.columns)

    if expected_cols != actual_cols:
        missing = expected_cols - actual_cols
        unexpected = actual_cols - expected_cols
        raise ValueError(
            f"Column mismatch: missing={missing}, unexpected={unexpected}"
        )

    df = df[list(config.column_spec.keys())] #sets column order

    for col, dtype in config.column_spec.items():
        if "datetime" in str(dtype):
            df[col] = pd.to_datetime(
                df[col], 
                format = config.date_kwargs.get('format'), 
                errors="coerce"
                )
        else:
            df[col] = df[col].astype(dtype, errors="ignore")
    df = df.sort_values(by=list(df.columns)).reset_index(drop=True)

    return df

def hash_df(df: pd.DataFrame, df_name: str) -> tuple[str, str]:
    """
    Intended for use with dataframes normalised using the normalise_df function
    Calculates a unique SHA-256 hash string for a normalised DataFrame
    Returns a tuple of the name of the dataframe and the hash string
    """
    row_bytes = pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes()
    hash_key = hashlib.sha256(row_bytes).hexdigest()

    return df_name, hash_key

def metadata_append():
    pass