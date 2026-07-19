from dataclasses import dataclass, field
from typing import Callable, cast
import pandas as pd


DOWNLOAD_DIR: str = "/home/john/projects/spend_over_25/downloaded_data/"

@dataclass
class ProviderConfig:
    date_col: str
    read_kwargs: dict = field(default_factory = dict)
    date_kwargs: dict = field(default_factory = dict)
    post_process: Callable[[pd.DataFrame], pd.DataFrame] | None = None   

def drop_blank_col(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns = df.columns[0])

def drop_blank_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(how="all").reset_index(drop=True)

PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    "RWY": ProviderConfig(date_col = 'Date', 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'}), #bucks, handled separately
    "RN5": ProviderConfig(date_col = 'Date', 
                          read_kwargs={"skiprows":3}, 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'}), #Hampshire hosps
    "R1F": ProviderConfig(date_col = 'Date', 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'}), #isle of wight
    "RTH": ProviderConfig(date_col = 'Invoice Creation Date',
                          date_kwargs={'errors':'raise', 'format':'%d-%b-%Y'}), #Oxford uni
    "RHU": ProviderConfig(date_col = 'Date', 
                          read_kwargs={"header":0}, 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'}, 
                          post_process = drop_blank_rows), #portsmouth
    "RHW": ProviderConfig(date_col = 'Date Paid', 
                          read_kwargs={"index_col":0, "skiprows":1}, 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'}, 
                          post_process= drop_blank_col), #rbft
    "RHM": ProviderConfig(date_col = 'Date\n(payment date)', 
                          read_kwargs={"skiprows":2}, 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'}), #Sotn Uni
}

def read_rwy(file_path: str) -> pd.DataFrame:
    sheets = pd.read_excel(file_path, sheet_name=None) #returns a dictionary of df per sheet
    return pd.concat(
        [df.assign(month=sheet) for sheet, df in sheets.items()],
        ignore_index = True,
    )

def find_header_xlsx(file_path: str, date_col: str) -> int:
    preview = pd.read_excel(file_path, header = None, nrows = 5)
    header_row: int | None = None
    
    for i, row in preview.iterrows():
        if date_col in row.astype(str).values:
            header_row = cast(int,i)
            break
    
    if header_row is None: 
        message = (f"Search for header failed, could not locate {date_col} in {file_path}")
        raise ValueError(message)
    return header_row

def read_rth(file_path: str, config = PROVIDER_CONFIGS['RTH']) -> pd.DataFrame:
    header_row = find_header_xlsx(file_path=file_path, date_col = config.date_col)
    return pd.read_excel(file_path, header = header_row)

CUSTOM_READERS: dict[str, Callable[[str], pd.DataFrame]] = {
    "RWY": read_rwy,
    "RTH": read_rth,
    #scales for more strange configs if needed
}