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
    column_spec: dict = field(default_factory = dict)   

def drop_blank_col(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns = df.columns[0])

def drop_blank_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(how="all").reset_index(drop=True)

PROVIDER_CONFIGS: dict[str, ProviderConfig] = {
    "RWY": ProviderConfig(date_col = 'Date', 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'},
                          column_spec = {
                              'Department Family':'str',
                              'Entity':'str',
                              'Date':'datetime64[ns]',
                              'Transaction number':'str',
                              'Supplier Name':'str',
                              'Expense type':'str',
                              'Expense area':'str',
                              'Amount':'float',
                          }), 
    "RN5": ProviderConfig(date_col = 'Date', 
                          read_kwargs={"skiprows":3}, 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'},
                          column_spec={
                              'Department Family':'str',
                              'Entity':'str',
                              'Date':'datetime64[ns]',
                              'Expense Type':'str',
                              'Expense Area':'str',
                              'Supplier':'str',
                              'Transaction Number':'str',
                              'AP Amount':'float',
                              'Description':'str',
                              'Supplier Postcode':'str',
                              'Supplier type':'str',
                              'Contract Number':'str',
                              'Project code':'str',
                              'Expenditure type':'str',
                              'VAT Registration Number':'str',
                              'Purchase Invoice Number':'str',
                          }), #Hampshire hosps
    "R1F": ProviderConfig(date_col = 'Date', 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'},
                          column_spec={
                              'Department Family': 'str',
                              'Entity':'str',
                              'Date':'datetime64[ns]',
                              'Expense Type':'str',
                              'Expense Area':'str',
                              'Supplier':'str',
                              'Transaction Number':'str',
                              'AP Amount':'float'
                          }), #isle of wight
    "RTH": ProviderConfig(date_col = 'Invoice Creation Date',
                          date_kwargs={'errors':'raise', 'format':'%d-%b-%Y'},
                          column_spec = {
                              'Business Unit':'str',
                              'Invoice No':'str',
                              'Voucher No':'int',
                              'Invoice Date':'datetime64[ns]',
                              'Invoice Amount':'float',
                              'Invoice Creation Date':'datetime64[ns]',
                              'Supplier Type':'str',
                              'Supplier Name':'str',
                          }), #Oxford uni
    "RHU": ProviderConfig(date_col = 'Date', 
                          read_kwargs={"header":0}, 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'}, 
                          post_process = drop_blank_rows,
                          column_spec = {
                              'Department Family':'str',
                              'Entity':'str',
                              'Date':'datetime64[ns]',
                              'Expense Type':'str',
                              'Expense Area':'str',
                              'Supplier':'str',
                              'Transaction Number':'str',
                              'AP Amount':'float',
                          }), #portsmouth
    "RHW": ProviderConfig(date_col = 'Date Paid', 
                          read_kwargs={"index_col":0, "skiprows":1}, 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'}, 
                          post_process= drop_blank_col,
                          column_spec={
                              'Accounting Year':'int',
                              'Sub Ledger Description':'str',
                              'Period (Date Paid)':'int',
                              'Date Paid':'datetime64[ns]',
                              '15AN - Level 15 Account Name':'str',
                              '15CCN - Level 15 Cost Centre Name':'str',
                              'Supplier Name':'str',
                              'Our Reference':'str',
                              'Transaction Status':'str',
                              'Analysed Gross':'float',
                          }), #rbft
    "RHM": ProviderConfig(date_col = 'Date\n(payment date)', 
                          read_kwargs={"skiprows":2}, 
                          date_kwargs={'errors':'raise', 'format':'%d/%m/%Y'},
                          column_spec={
                              'Department Family':'str',
                              'Entity':'str',
                              'Supplier':'str',
                              'Transaction Number\n(invoice number)':'str',
                              'Date\n(payment date)':'datetime64[ns]',
                              'Amount':'float',
                              'Currency':'str',
                          }), #Sotn Uni
}

def read_rwy(file_path: str) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(file_path, sheet_name = None)
    return sheets

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

def read_rth(file_path: str) -> dict[str,pd.DataFrame]:
    config = PROVIDER_CONFIGS['RTH']
    header_row = find_header_xlsx(file_path=file_path, date_col = config.date_col)
    return pd.read_excel(file_path, header = header_row, sheet_name = None)

CUSTOM_READERS: dict[str, Callable[[str], dict[str,pd.DataFrame]]] = {
    "RTH": read_rth,
    #scales for more strange configs if needed
}