import pandas as pd
import logging

from os import listdir
from os.path import isfile, join
from typing import Callable
from dataclasses import dataclass, field

from raw_to_bronze.bronze_config import PROVIDER_CONFIGS, READERS, DOWNLOAD_DIR, ProviderConfig

x = pd.read_excel('/home/john/projects/spend_over_25/downloaded_data/RHM/Expenditure-over-25000-February-2026.xlsx', skiprows=2)

print(x.columns)