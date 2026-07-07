import pandas as pd
import logging
from os import listdir
from os.path import isfile, join

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('initial_clean.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)



def raw_files_to_df(dir_name: str) -> dict[str,list]:
    """
    Goes through a directory and converts all xlsx or csv files to pandas DataFrames
    Args: 
        dir_name (str) the name of the directory to be searched
    
    Returns:
        dict(str, list): key is name of the searched directory, value is list of dataframes
    """

    #Note to self, this is probably going to need additional params to allow for thinks like skipping lines
    #And/or dealing with merged cell

    def read_with_logging(file_path: str) -> pd.DataFrame|None:
        logger.info("processing: %s",file_path)
        try:
            if file_path.endswith("xlsx"):
                file_df = pd.read_excel(file_path)
            elif file_path.endswith("csv"):
                file_df = pd.read_csv(file_path)
            else:
                raise ValueError(f"file: {file_path} not of an accepted type")
        except Exception:
            logger.exception("load error in %s", file_path)
            return None                    
        else:
            logger.info("success: %s", file_path)
            return file_df

    raw_dir: str = "/home/john/projects/spend_over_25/downloaded_data/"
    full_dir: str = join(raw_dir,dir_name)

    if dir_name not in listdir(raw_dir):
        raise ValueError(f"Value error: {dir_name} not found in raw data directory")
    else:
        file_list: list = [f for f in listdir(full_dir) if isfile(join(full_dir, f)) and f.endswith(("xlsx","csv"))]
        df_list: list = [df for f in file_list if (df := read_with_logging(join(full_dir,f))) is not None]
        return {(f"{dir_name}"): df_list}