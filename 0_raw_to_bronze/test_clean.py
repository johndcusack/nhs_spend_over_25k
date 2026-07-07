import pandas as pd
import logging
from os import listdir
from os.path import isfile, join
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('initial_clean.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

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

def raw_files_to_df(dir_name: str) -> dict[str,list]:
    """
    Goes through a directory and converts all xlsx or csv files to pandas DataFrames
    Args: 
        dir_name (str) the name of the directory to be searched
    
    Returns:
        dict(str, list): key is name of the searched directory, value is list of dataframes
    """

    def read_with_logging(file_path: str, config: ProviderConfig, reader: Callable|None) -> pd.DataFrame|None:
        logger.info("processing: %s",file_path)
        try:
            if reader is not None:
                file_df = reader(file_path)
            elif file_path.endswith("xlsx"):
                file_df = pd.read_excel(file_path, **config.read_kwargs)
            elif file_path.endswith("csv"):
                file_df = pd.read_csv(file_path, **config.read_kwargs)
            else:
                raise ValueError(f"file: {file_path} not of an accepted type")
            if config.post_process is not None:
                file_df = config.post_process(file_df)
        except Exception:
            logger.exception("load error in %s", file_path)
            return None                    
        else:
            logger.info("success: %s", file_path)
            return file_df

    raw_dir: str = "/home/john/projects/spend_over_25/downloaded_data/"
    full_dir: str = join(raw_dir,dir_name)
    config = PROVIDER_CONFIGS[dir_name] #fails loudly if a directory name is passed without a configuration
    reader = READERS.get(dir_name)
    if dir_name not in listdir(raw_dir):
        raise ValueError(f"Value error: {dir_name} not found in raw data directory")
    else:
        file_list: list = [f for f in listdir(full_dir) if isfile(join(full_dir, f)) and f.endswith((".xlsx",".csv"))]
        df_list: list = [df for f in file_list if (df := read_with_logging(join(full_dir,f), config=config, reader= reader)) is not None]
        return {(f"{dir_name}"): df_list}