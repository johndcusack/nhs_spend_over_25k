import pandas as pd
import logging
import warnings

from os import listdir
from os.path import isfile, join
from typing import Callable
from dataclasses import dataclass, field

from prestaging.prestaging_config import PROVIDER_CONFIGS, CUSTOM_READERS, DOWNLOAD_DIR, ProviderConfig

# Set up logging 

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('initial_clean.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

@dataclass
class LoadSummary:
    attempted_files: int = 0

    failed_files: list[str] = field(default_factory=list)

    attempted_sheets: int = 0
    succeeded_sheets: int = 0
    failed_sheets: list[str] = field(default_factory=list)

    @property
    def failed_file_count(self) -> int:
        return len(self.failed_files)

    @property
    def failed_sheet_count(self) -> int:
        return len(self.failed_sheets)

    def __str__(self) -> str:
        return (f"attempted_files={self.attempted_files}, "
                f"succeeded_files={self.attempted_files-self.failed_file_count}\n"
                f"failed={self.failed_file_count} ({self.failed_files})\n"
                f"attempted_sheets={self.attempted_sheets}, succeeded_sheets={self.succeeded_sheets}\n"
                f"sheet failures={self.failed_sheet_count} ({self.failed_sheets})")
    
# Main process function

def raw_files_to_df(dir_name: str) -> tuple[dict[str,pd.DataFrame], LoadSummary]:
    """
    Goes through a directory and converts all xlsx or csv files to pandas DataFrames
    Args: 
        dir_name (str) the name of the directory to be searched
    
    Returns:
        dict(str, list): key is name of the searched directory and the year-month of the file, value is a dataframe
    """

    def read_with_logging(file_path: str, config: ProviderConfig, reader: Callable|None) -> dict[str, pd.DataFrame]:
        logger.info("processing: %s",file_path)

        if not file_path.endswith((".xlsx", ".csv")):
            message = f"file: {file_path} not of an accepted type"
            logger.error(message)
            raise ValueError(message)

        try:
            if reader is not None:
                file_dict = reader(file_path)
            elif file_path.endswith("xlsx"):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    file_dict = pd.read_excel(file_path, sheet_name = None, **config.read_kwargs)
            else:
                file_dict = {"csv": pd.read_csv(file_path, **config.read_kwargs)}            
            if config.post_process is not None:
                for key, value in file_dict.items(): 
                    file_dict[key] = config.post_process(value)
        except Exception:
            message = f"load error in {file_path}"
            logger.exception(message)
            raise RuntimeError(message)    
        else:
            logger.info("success: %s", file_path)
            for key, value in file_dict.items():
                file_dict[key] = value.rename(columns=lambda x: x.strip())
            return file_dict

    def identify_df_period(df: pd.DataFrame, config:ProviderConfig, dir_name:str, file_path: str, sheet_id: str) -> str:
        try: 
            dates = pd.to_datetime(df[config.date_col], **config.date_kwargs)
        except Exception:
            message = f"Key Error: {config.date_col} not present in {file_path} - sheet ID: {sheet_id}"
            logger.exception(message)
            raise KeyError(message)

        year_month = dates.dt.to_period('M')
        unique_year_month = year_month.dropna().unique()
        
        if len(unique_year_month) != 1:
            months_seen = unique_year_month.astype(str)
            message: str = f"Expected single month in file, found {months_seen} for {file_path} - sheet ID: {sheet_id}"
            logger.error(message)
            raise ValueError(message)

        return f"{dir_name}_{unique_year_month[0]}"

    full_dir: str = join(DOWNLOAD_DIR,dir_name)
    config = PROVIDER_CONFIGS[dir_name] #fails loudly if a directory name is passed without a configuration
    reader = CUSTOM_READERS.get(dir_name)

    if dir_name not in listdir(DOWNLOAD_DIR):
        message: str = f"Value error: {dir_name} not found in raw data directory"
        logger.error(message)
        raise ValueError(message)
    
    else:
        file_list: list[str] = [f for f in listdir(full_dir) if isfile(join(full_dir, f)) and f.endswith((".xlsx",".csv"))]
        dataframes: dict[str, pd.DataFrame] = {}

        summary = LoadSummary()

        for f in file_list:
            file_path: str = join(full_dir,f)
            summary.attempted_files +=1
            
            try: 
                file_dict = read_with_logging(file_path=file_path, config=config, reader=reader)
                
            except Exception:
                logger.error("skipping %s, see log for details",file_path)
                summary.failed_files.append(file_path)
                continue

            for key, value in file_dict.items():
                summary.attempted_sheets +=1
                try:
                    table_name = identify_df_period(df=value, config=config, dir_name=dir_name, file_path=file_path, sheet_id=key)
                except Exception:
                    failure = file_path+" : "+key
                    logger.error("skipping %s, see log for details",failure)
                    summary.failed_sheets.append(failure)
                    continue

                if table_name in dataframes:
                    message: str = f"Duplicate table key '{table_name}. {f} produced a key already populated in this batch"
                    logger.error(message)
                    raise ValueError(message)
            
                dataframes[table_name] = value
                summary.succeeded_sheets +=1

        return dataframes, summary    