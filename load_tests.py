import pandas as pd
import logging

from os import listdir
from os.path import isfile, join
from typing import Callable
from dataclasses import dataclass, field

from raw_to_bronze.bronze_config import PROVIDER_CONFIGS, READERS, DOWNLOAD_DIR, ProviderConfig

x = pd.read_excel('/home/john/projects/spend_over_25/downloaded_data/RTH/25k-invoices-november-2025.xlsx')

print(x.columns)