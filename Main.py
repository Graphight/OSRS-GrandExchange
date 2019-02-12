
# Libraries
import warnings
import pandas as pd
import statsmodels.api as sm

import itertools
import logging
import matplotlib

from time import sleep
from matplotlib import pyplot as plt
from DataCollection import collect_item_graph_data_and_write_to_csv, collect_item_ids, collect_promising_items


# =================================================
#  ========== PRELIM : CONFIG MATPLOTLIB ==========
# =================================================
warnings.filterwarnings("ignore")
plt.style.use("fast")
matplotlib.rcParams["axes.labelsize"] = 14
matplotlib.rcParams["xtick.labelsize"] = 12
matplotlib.rcParams["ytick.labelsize"] = 12
matplotlib.rcParams["text.color"] = "k"
matplotlib.rcParams["figure.figsize"] = 18, 8


# =================================================
#     ========== STEP ONE : SETUP ==========
# =================================================

# Important
BASE_URL = "http://services.runescape.com/m=itemdb_oldschool"
logger = logging.getLogger("OSRS")
logger.setLevel("DEBUG")

# Endpoints
ENDPOINT_CATALOGUE_CATEGORY = "/api/catalogue/category.json?category=1"
ENDPOINT_CATALOGUE_ITEMS = "/api/catalogue/items.json?category=1&alpha={}&page={}"
ENDPOINT_CATALOGUE_DETAIL = "/api/catalogue/detail.json?item={}"
ENDPOINT_GRAPHS = "/api/graph/{}.json"


# =================================================
#     ========== STEP TWO : DISCOVERY ==========
# =================================================


# Collect item ids
file_name = "ItemIds.csv"
collect_item_ids(BASE_URL, ENDPOINT_CATALOGUE_CATEGORY, ENDPOINT_CATALOGUE_ITEMS, file_name)

df_items = pd.read_csv(file_name)
promising_items = collect_promising_items(BASE_URL, df_items, ENDPOINT_CATALOGUE_DETAIL)

print(promising_items)






























