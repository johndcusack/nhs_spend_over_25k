import pandas as pd
import logging

from os import listdir
from os.path import isfile, join
from typing import Callable

from raw_to_bronze.bronze_config import PROVIDER_CONFIGS, READERS, DOWNLOAD_DIR, ProviderConfig

# Set up logging 

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('initial_clean.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Main process function

def raw_files_to_df(dir_name: str) -> dict[str,pd.DataFrame]:
    """
    Goes through a directory and converts all xlsx or csv files to pandas DataFrames
    Args: 
        dir_name (str) the name of the directory to be searched
    
    Returns:
        dict(str, list): key is name of the searched directory and the year-month of the file, value is a dataframe
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

    def identify_df_period(df: pd.DataFrame, config:ProviderConfig, dir_name:str, file_path: str):
        try: 
            dates = pd.to_datetime(df[config.date_col], errors='raise')
        except Exception:
            logger.exception(f"Key Error: {config.date_col} not present in {file_path}")
            return None

        year_month = dates.dt.to_period('M')
        unique_year_month = year_month.unique()

        if len(unique_year_month) != 1:
            message: str = f"Expected single month in file, found {len(unique_year_month)} for {file_path}"
            logger.error(message)
            raise ValueError(message)

        return f"{dir_name}_{unique_year_month[0]}"


    full_dir: str = join(DOWNLOAD_DIR,dir_name)
    config = PROVIDER_CONFIGS[dir_name] #fails loudly if a directory name is passed without a configuration
    reader = READERS.get(dir_name)
    if dir_name not in listdir(DOWNLOAD_DIR):
        message: str = f"Value error: {dir_name} not found in raw data directory"
        logger.error(message)
        raise ValueError(message)
    
    else:
        file_list: list[str] = [f for f in listdir(full_dir) if isfile(join(full_dir, f)) and f.endswith((".xlsx",".csv"))]
        dataframes: dict[str, pd.DataFrame] = {}

        for f in file_list:
            file_path: str = join(full_dir,f)
            df = read_with_logging(file_path=file_path, config=config, reader=reader)
            if not isinstance(df, pd.DataFrame):
                continue #issue already logged
            table_name = identify_df_period(df=df,config=config,dir_name=dir_name, file_path=file_path)
            if table_name is None:
                continue #issue already logged
            if table_name in dataframes:
                message: str = f"Duplicate table key '{table_name}. {f} produced a key already populated in this batch"
                logger.error(message)
                raise ValueError(message)
            else:
                dataframes[table_name] = df

        return dataframes





    