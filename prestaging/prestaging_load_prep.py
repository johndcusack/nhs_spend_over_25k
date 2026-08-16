import pandas as pd
from prestaging.prestaging_config import PROVIDER_CONFIGS, CUSTOM_READERS, DOWNLOAD_DIR, ProviderConfig
# rework config to have a column order for sorting each org's columns
# 
def normalise_df(df: pd.DataFrame, config: ProviderConfig):
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

def hash_df(df: pd.DataFrame):
    pass

def metadata_append():
    pass