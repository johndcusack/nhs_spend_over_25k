from dataclasses import dataclass, field
from typing import Callable
import pandas as pd

@dataclass
class ProviderConfig:
    read_kwargs: dict = field(default_factory = dict)
    post_process: Callable[[pd.DataFrame], pd.DataFrame] | None = None

def drop_blank_col(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns = df.columns[0])

def drop_blank_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(how="all").reset_index(drop=True)

PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    "RWY": ProviderConfig(), #bucks, handled separately
    "RN5": ProviderConfig(read_kwargs={"skiprows":3}), #Hampshire hosps
    "R1F": ProviderConfig(), #isle of wight
    "RTH": ProviderConfig(read_kwargs={"skiprows":2}), #Oxford uni
    "RHU": ProviderConfig(read_kwargs={"header":0}, post_process = drop_blank_rows), #portsmouth
    "RHW": ProviderConfig(read_kwargs={"index_col":0}, post_process= drop_blank_col), #rbft
    "RHM": ProviderConfig(read_kwargs={"skiprows":2}), #Sotn Uni
}

def read_bucks(file_path: str) -> pd.DataFrame:
    sheets = pd.read_excel(file_path, sheet_name=None) #returns a dictionary of df per sheet
    return pd.concat(
        [df.assign(month=sheet) for sheet, df in sheets.items()],
        ignore_index = True,
    )

READERS: dict[str, Callable[[str], pd.DataFrame]] = {
    "RWY": read_bucks,
    #scales for more strange configs if needed
}